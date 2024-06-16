import ctypes
import datetime
import html
import logging
import os
import re
import time
from tkinter import END
import pymem
import pymem.process

from mem_edit import Process



from classes.oppbot_faction import Faction
from classes.oppbot_match_type import MatchType
from classes.oppbot_settings import Settings
from classes.oppbot_player import Player
from classes.oppbot_replay_parser import ReplayParser
from classes.oppbot_stats_request import StatsRequest
from classes.oppbot_overlay_templates import OverlayTemplates
from classes.oppbot_ucs import UCS


class GameData():
    "Contains information about the current COH1 game and players."

    def __init__(self, irc_client=None, settings=None, tkconsole = None):
        "Instanciates a new object of type GameData"

        self.settings = settings
        if not settings:
            self.settings = Settings()

        # Local reference to the IRC client
        self.irc_client = irc_client

        # Local reference to tkconsole
        self.tkconsole = tkconsole

        # shared handle to process
        self.pm = None

        # Replay Data Default Values
        self.playerList = []
        self.numberOfHumans = 0
        self.numberOfComputers = 0
        self.easyCPUCount = 0
        self.normalCPUCount = 0
        self.hardCPUCount = 0
        self.expertCPUCount = 0
        self.numberOfPlayers = 0
        self.slots = 0
        self.matchType = MatchType.CUSTOM
        self.gameStartedDate = None

        self.randomStart = None
        self.highResources = None
        self.VPCount = None
        self.automatch = None
        self.mapName = None
        self.mapNameFull = ""
        self.modName = None
        self.mapDescription = None
        self.mapDescriptionFull = ""
        self.gameDescriptionString = ""


        # application state indicators
        self.coh_running = False
        self.game_in_progress = False
        self.live_game = False
        self.replay_full_path = ""


        # This holds a list of IRC string outputs.
        self.ircStringOutputList = []

    def clear_data(self):
        "Clears all the variable information in the GameData instance."

        self.playerList : Player = []
        self.numberOfHumans = 0
        self.numberOfComputers = 0
        self.easyCPUCount = 0
        self.normalCPUCount = 0
        self.hardCPUCount = 0
        self.expertCPUCount = 0
        self.numberOfPlayers = 0
        self.slots = 0
        self.matchType = MatchType.CUSTOM
        self.gameStartedDate = None
        self.randomStart = None
        self.highResources = None
        self.VPCount = None
        self.automatch = None
        self.mapName = None
        self.mapNameFull = ""
        self.modName = None
        self.mapDescription = None
        self.mapDescriptionFull = ""
        self.gameDescriptionString = ""

        # This holds a list of IRC string outputs.
        self.ircStringOutputList = []

    def get_data_from_game(self):
        "Attempts to get all the COH information from memory."

        # First Clear all data that can be aquired from the game
        # self.clear_data()

        # Check if company of heroes is running if not return false
        if not self.get_COH_memory_address():
            return False

        # Check for in game or main menu
        self.check_for_game_in_progress()

        # Check if a game is currently in progress.
        # replayParser = self.Get_replayParser_BySearch()
        live_replay = self.get_replay_parser_by_pointer()
        replay_parser = live_replay
        if not live_replay:
            # Check if PLAYBACK:filename.rec exists
            # If so assume game is a replay and in progress
            recorded_replay = self.get_replay_parser_from_memory_replays()
            replay_parser = recorded_replay
            if not recorded_replay:
                return False

        # if new data availble
        self.clear_data()

        self.gameStartedDate = replay_parser.localDate
        self.randomStart = replay_parser.randomStart

        self.highResources = replay_parser.highResources
        self.VPCount = replay_parser.VPCount
        self.automatch = False
        # Korean replays don't contain a matchType string
        if replay_parser.matchType:
            if replay_parser.matchType.lower() == "automatch":
                self.automatch = True


        self.mapName = replay_parser.mapName
        self.mapDescription = replay_parser.mapDescription
        self.modName = replay_parser.modName

        for item in replay_parser.playerList:
            name = item.get('name')
            faction_name = item.get('faction')
            player = Player(name=name, faction_name=faction_name)
            self.playerList.append(player)

        logging.info(self.playerList)
        logging.info(len(self.playerList))

        # Get the number of computers if any by name
        # this number could be wrong is a player decided to name
        # themselves the same as a computer
        # therefore we check this again after we recieve stats
        # to see if that player had a steam number

        cpuCounter = 0
        humanCounter = 0

        for item in self.playerList:
            if ("CPU" in item.name):
                cpuCounter += 1
            else:
                # ignore empty slots with no faction
                if (item.faction):
                    humanCounter += 1

        logging.info(cpuCounter)

        statList = []

        if self.live_game:
            # Don't bother trying to get steam numbers and stats if replay
            statList = self.get_stats_from_game()
            # check if number of stats recieved is equal to or greater than
            # the number of humans, if not stats collection has failed
            # return false so the caller can try again later.
            if not (len(statList) >= humanCounter):
                return False

        for player in self.playerList:
            if statList:
                for stat in statList:
                    try:
                        if not stat:
                            # if the server doesn't respond with stats
                            return False
                        alias = str(stat.alias).encode('utf-16le')
                        name = str(player.name).encode('utf-16le')
                        if alias == name:
                            player.stats = stat
                    except Exception as e:
                        logging.error(str(e))
                        logging.exception("Stack : ")

                    steamNumber = self.settings.data.get('steamNumber')
                    ps = player.stats
                    if ps:
                        if steamNumber == ps.steamNumber:
                            self.settings.data['steamAlias'] = ps.alias
                            self.settings.save()

                # try to do some debugging here.
                logging.info(player)

        humans = sum(item.stats is not None for item in self.playerList)
        self.numberOfHumans = humans

        cpuCounter = 0
        easyCounter = 0
        normalCounter = 0
        hardCounter = 0
        expertCounter = 0

        for item in self.playerList:
            if (item.stats is None):
                if ("CPU" in item.name):
                    cpuCounter += 1
                if ("Easy" in item.name):
                    easyCounter += 1
                if ("Normal" in item.name):
                    normalCounter += 1
                if ("Hard" in item.name):
                    hardCounter += 1
                if ("Expert" in item.name):
                    expertCounter += 1


        self.numberOfPlayers = cpuCounter + self.numberOfHumans
        self.easyCPUCount = easyCounter
        self.normalCPUCount = normalCounter
        self.hardCPUCount = hardCounter
        self.expertCPUCount = expertCounter

        self.slots = len(replay_parser.playerList)

        # Set the current MatchType

        self.matchType = MatchType.CUSTOM
        if (int(self.numberOfComputers) > 0):
            self.matchType = MatchType.CUSTOM
        if self.automatch:
            if (0 <= int(self.slots) <= 2):
                if (int(self.numberOfComputers) == 0):
                    self.matchType = MatchType.ONES
            if (3 <= int(self.slots) <= 4):
                if (int(self.numberOfComputers) == 0):
                    self.matchType = MatchType.TWOS
            if (5 <= int(self.slots) <= 6):
                if (int(self.numberOfComputers) == 0):
                    self.matchType = MatchType.THREES
            if (7 <= int(self.slots) <= 8):
                if (int(self.numberOfComputers) == 0):
                    self.matchType = MatchType.FOURS

        return True

    def check_for_game_in_progress(self) -> bool:

        if not self.pm:
            return

        listOfPointers = []

        process_name = "Localizer.dll"
        address = 0x00013478
        offsets = [0xA4, 0x0, 0x0]
        listOfPointers.append([process_name ,address, offsets])

        process_name = "Localizer.dll"
        address = 0x00013478
        offsets = [0xA4, 0x8, 0x0]
        listOfPointers.append([process_name ,address, offsets])

        game_in_progress = False

        base_address = pymem.process.module_from_name(self.pm.process_handle, process_name).lpBaseOfDll

        rd = None

        for count, item in enumerate(listOfPointers):

            ad = self.get_pointer_address(base_address + item[1], item[2])
            actualMemoryAddress = ad

            if actualMemoryAddress:
                try:
                    rd = self.pm.read_bytes(actualMemoryAddress, 6)
                except Exception as e:
                    logging.info(e)
                if rd:
                    try:
                        # When the menu screen is available the version number
                        # will be in memory "2.700.2.43" - I just get the first
                        # 6 bytes of 2 byte wide utf-16le chars
                        if "2.7" in rd.decode('utf-16le') :
                            game_in_progress = False
                            self.game_in_progress = game_in_progress
                            return False
                        else:
                            # if not able to find version string
                            # not in the main menu
                            game_in_progress = True
                            self.game_in_progress = game_in_progress

                    except Exception as e:
                        # exception maybe thrown due to being unable to
                        # read the random bytes at this location when  
                        # not in menu
                        game_in_progress = True
                        self.game_in_progress = game_in_progress

        # In the event that rd was none due to read_bytes errors
        # the game is more likely to be in progress than not.
        self.game_in_progress = True
        return self.game_in_progress


    def get_game_description_string(self) -> str:
        "Produces a single-line game description string."

        if not self.playerList:
            return

        offset = time.timezone
        if (time.localtime().tm_isdst == 0):
            offset = time.timezone
        else:
            time.altzone

        offset = offset / 60 / 60 * -1
        hours = offset
        hours_added = datetime.timedelta(hours=hours)

        try:
            UTC_corrected_start_time = self.gameStartedDate + hours_added
        except TypeError:
            UTC_corrected_start_time = None

        gameStarted = str(UTC_corrected_start_time)
        channelName = self.settings.data.get('channel')

        # Get the map full name from ucs file this takes time and so
        # should only be called when output is intended.

        self.get_mapNameFull_from_UCS_file()

        try:
            numberOfHumans = str(int(self.numberOfHumans))
            numberOfComputers = str(int(self.numberOfComputers))
            numberOfPlayers = str(int(self.numberOfPlayers))
            slots = str(int(self.slots))
            randomStart = str(int(self.randomStart))
            highResources = str(int(self.highResources))
            VPCount = str(int(self.VPCount))
            automatch = str(int(self.automatch))
            mapNameFull = str(self.mapNameFull)
            modName = str(self.modName)

            message = (
                f"!start,{channelName},{gameStarted},{numberOfHumans},"
                f"{numberOfComputers},{numberOfPlayers},{slots},{randomStart},"
                f"{highResources},{VPCount},{automatch},{mapNameFull},"
                f"{modName}"
                )

        except Exception as e:
            logging.error("Problem Creating Game Description")
            logging.exception("Exception : ")
            logging.error(str(e))
            return None

        for count, item in enumerate(self.playerList):
            steamNumber = ""
            if item.stats:
                steamNumber = item.stats.steamNumber
            else:
                steamNumber = item.name

            faction = ""
            if item.faction:
                faction = item.faction.name
            team = "0"
            if count >= (len(self.playerList)/2):
                team = "1"

            message += f",{str(steamNumber)},{str(faction)},{str(team)}"

        self.gameDescriptionString = message
        return self.gameDescriptionString

    def get_mapDescriptionFull_from_UCS_file(self):
        "mapDescriptionFull will be None until resolved."

        try:
            ucs = UCS(settings=self.settings)
            self.mapDescriptionFull = ucs.compare_UCS(self.mapDescription)

        except Exception as e:
            logging.error("Problem in GetMapDescription")
            logging.exception("Exception : ")
            logging.error(str(e))

    def get_mapNameFull_from_UCS_file(self):
        "mapNameFull will be None until resolved."

        try:
            ucs = UCS(settings=self.settings)
            self.mapNameFull = ucs.compare_UCS(self.mapName)
        except Exception as e:
            logging.error("Problem in GetMapNameFull")
            logging.exception("Exception : ")
            logging.error(str(e))

    def get_pointer_address(self, base: int, offsets: list) -> int | None:
        "Gets memory address from a pointer address (base)"

        if not self.pm:
            return

        try:
            addr = self.pm.read_int(base)
            for count, offset in enumerate(offsets):
                    if count == len(offsets) - 1:
                        break
                    addr = self.pm.read_int(addr + offset)
            return addr + offsets[-1]

        except Exception as e:
            return None

    def get_COH_memory_address(self) -> bool:
        "Gets the active process for RelicCOH.exe"

        try:
            self.pm = pymem.Pymem("RelicCOH.exe")
        except Exception as e:
            self.pm = None
            self.coh_running = False
            return False
        if self.pm:
            self.coh_running = True
            return True

    def get_replay_parser_by_pointer(self) -> ReplayParser | None:
        "Gets an instance of the replayParser containing COH game info."

        if not self.pm:
            return

        base_address = self.pm.base_address

        myListOfCOHRECPointers = []
        # 1
        cohrecReplayAddress = 0x00902030
        cohrecOffsets = [0x28, 0x160, 0x4, 0x84, 0x2C, 0x110, 0x0]
        myListOfCOHRECPointers.append([cohrecReplayAddress, cohrecOffsets])

        # 2
        cohrecReplayAddress = 0x00902030
        cohrecOffsets = [0x28, 0x160, 0x4, 0x84, 0x24, 0x110, 0x0]
        myListOfCOHRECPointers.append([cohrecReplayAddress, cohrecOffsets])

        coh_rec_present = False

        rd = None

        for count, item in enumerate(myListOfCOHRECPointers):

            ad = self.get_pointer_address(base_address + item[0], item[1])
            actualCOHRECMemoryAddress = ad

            if actualCOHRECMemoryAddress:
                try:
                    rd = self.pm.read_bytes(actualCOHRECMemoryAddress, 4000)
                except Exception as e:
                    print(e)
                if rd:
                    if rd[4:12] == bytes("COH__REC".encode('ascii')):
                        # if COH__REC is present then the 
                        # game is live meaning it is not a replay
                        # and is recording the game state to memory.
                        coh_rec_present = True
                        self.live_game = coh_rec_present
                        rd = bytearray(rd)
                        rp = ReplayParser(settings=self.settings)
                        rp.data = bytearray(rd)
                        success = rp.process_data()
                        if success:
                            logging.info(
                                "Successfully Parsed Replay Data.")
                            return rp
                        logging.info(
                            "Replay Data did not parse correctly.")
                        self.live_game = False
                        return None
        # if unable to find COH__REC in the memory then set live game to false
        self.live_game = coh_rec_present

    def get_replayParser_by_search(self) -> ReplayParser | None:
        "Gets an instance of the replayParser containing COH game info."

        if self.pm:
            with Process.open_process(self.pm.process_id) as p:

                searchString = bytearray("COH__REC".encode('ascii'))
                buff = bytes(searchString)

                replayMemoryAddress = p.search_all_memory(buff)

                if replayMemoryAddress:
                    for address in replayMemoryAddress:
                        # There should be only one COH__REC in memory
                        # if the game is running
                        self.live_game = True
                        try:
                            rd = self.pm.read_bytes(address-4, 4000)
                            rd = bytearray(rd)
                            rp = ReplayParser(settings=self.settings)
                            rp.data = bytearray(rd)
                            success = rp.process_data()
                            # Processing game data may not be successful
                            # if the memory is being moved
                            # by memory management
                            if success:
                                logging.info(
                                    "Successfully Parsed Replay Data.")
                                return rp
                            else:
                                logging.info(
                                    "Replay Data did not parse correctly.")
                                return None
                        except Exception as e:
                            if e:
                                pass

    def read_null_terminated_2_byte_string(self, data) -> str:
        "Reads a Utf-16 little endian character string."

        try:
            if data:
                dataIndex = 0
                characters = ""
                for character in data:
                    char = bytearray(data[dataIndex:dataIndex+2])
                    dataIndex += 2
                    if bytearray(char) == bytearray(b"\x00\x00"):
                        break
                    characters += bytearray(char).decode('utf-16le')

                return characters
        except Exception as e:
            print(e)

    def get_replay_parser_from_memory_replays(self):

        if not self.pm:
            return

        baseAddress = self.pm.base_address

        replay_path_pointers = []

        # 1
        replayAddress = 0x008F80E0
        cohrecOffsets = [0x0, 0x90, 0x160, 0x4, 0xE90, 0x8CC, 0x0]
        replay_path_pointers.append([replayAddress, cohrecOffsets])

        # 2
        replayAddress = 0x009017E8
        cohrecOffsets = [0x1C, 0x0, 0xE8C, 0x8CC, 0x0]
        replay_path_pointers.append([replayAddress, cohrecOffsets])

        # 3
        replayAddress = 0x00901B4C
        cohrecOffsets = [0x84, 0x4, 0x160, 0x4, 0xE90, 0x8CC, 0x0]
        replay_path_pointers.append([replayAddress, cohrecOffsets])

        # 4
        replayAddress = 0x00902030
        cohrecOffsets = [0x28, 0x160, 0x4, 0xE90, 0x8CC, 0x0]
        replay_path_pointers.append([replayAddress, cohrecOffsets])

        for count, item in enumerate(replay_path_pointers):
            ad = self.get_pointer_address(baseAddress + item[0], item[1])
            actualMemoryAddress = ad

            if actualMemoryAddress:
                try:
                    rd = self.pm.read_bytes(actualMemoryAddress, 300)
                except Exception as e:
                    logging.error(e)
                if rd:
                    try:
                        replay_path = self.settings.data.get('playbackPath') + self.read_null_terminated_2_byte_string(rd)[9:]
                        self.replay_full_path = replay_path
                        return ReplayParser(filePath = replay_path, settings=self.settings)
                    except Exception as e:
                        logging.error(e)


    def send_to_tkconsole(self, message):
        "Sends a message to the output field of the GUI."

        try:
            # First strip characters outside of range
            # that cannot be handled by tkinter output field
            char_list = ''
            for x in range(len(message)):
                if ord(message[x]) in range(65536):
                    char_list += message[x]
            message = char_list
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")
        try:
            if self.tkconsole:
                self.tkconsole.insert(END, message + "\n")
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")

    def get_stats_from_game(self):
        "Provides stats from playerList names from game memory."

        if not self.pm:
            return
        
        with Process.open_process(self.pm.process_id) as p:
            steamnumber_list = []
            # steamNumberList.append(self.settings.data.get('steamNumber'))
            # add default value incase it isn't found.
            for player in self.playerList:
                name = bytearray(str(player.name).encode('utf-16le'))
                buff = bytes(name)
                if buff:
                    replayMemoryAddress = p.search_all_memory(buff)
                    for address in replayMemoryAddress:
                        try:
                            ad = address-56
                            dd = p.read_memory(ad, (ctypes.c_byte * 48)())
                            dd = bytearray(dd)
                            steamNumber = dd.decode('utf-16le').strip()
                            if "/steam/" in steamNumber:
                                int(steamNumber[7:24])
                                # throws exception if steamNumber
                                # is not a number
                                info = (
                                    f"Got steamNumber from memory "
                                    f"{str(steamNumber[7:24])}"
                                )
                                logging.info(info)
                                sNumber = str(steamNumber[7:24])
                                steamnumber_list.append(sNumber)
                                break
                        except Exception as e:
                            if e:
                                pass

                statList = []
                for item in steamnumber_list:
                    statRquest = StatsRequest(settings=self.settings)
                    stat = statRquest.return_stats(item)
                    statList.append(stat)
                return statList

    def test_output(self):
        "Produces text output according to Preformat."
        if not self.settings:
            self.settings = Settings()

        steamNumber = self.settings.data.get('steamNumber')
        statsRequest = StatsRequest(settings=self.settings)
        streamerStats = statsRequest.return_stats(str(steamNumber))
        streamerPlayer = Player(name=self.settings.data.get('channel'))
        streamerPlayer.stats = streamerStats
        if streamerPlayer.stats:
            output = (
                "Streamer Full Stat list formatted according"
                " to Custom Chat Output Preformat:"
            )
            if self.tkconsole:
                self.send_to_tkconsole(output)
            preformat = self.settings.data.get('chat_custom_pf')
            if self.tkconsole:
                self.send_to_tkconsole(preformat)

            for match in MatchType:
                for faction in Faction:
                    for value in streamerPlayer.stats.leaderboardData:
                        ld = streamerPlayer.stats.leaderboardData[value]
                        playerFaction = str(ld.faction)
                        if (playerFaction == str(faction)):
                            playerMatchtype = str(ld.matchType)
                            if (playerMatchtype == str(match)):
                                self.matchType = match
                                streamerPlayer.faction = faction
                                self.__produceOutput(streamerPlayer)

        else:
            output = (
                "I could not get stats from the stat server using steam# "
                f"{steamNumber} it might be down or the steam# might "
                "be invalid."
            )
            if self.tkconsole:
                self.send_to_tkconsole(output)

    def __produceOutput(self, streamerPlayer):
        sFD = self.populate_string_formatting_dictionary(streamerPlayer)
        cPFOS = self.settings.data.get('chat_custom_pf')
        theString = self.format_preformatted_string(cPFOS, sFD)
        outputList = list(self.split_by_n(theString, 500))
        for item in outputList:
            if self.tkconsole:
                self.send_to_tkconsole(item)

    def output_opponent_data(self):
        "Outputs game and player information according to formats."

        # Check for server contact, if denied do not output anything
        stats_request = StatsRequest()
        stats_request.return_stats(self.settings.data.get('steamNumber'))
        if stats_request.info:
            if "DENIED" in stats_request.info:
                message = "Unable to get data from the relic server."
                self.send_to_tkconsole(message)
                if stats_request.reason:
                    self.send_to_tkconsole(stats_request.reason)
                if stats_request.message:
                    self.send_to_tkconsole(stats_request.message)
                logging.error(message)
                return False
            if "OUTOFDATE" in stats_request.info:
                if stats_request.message:
                    self.send_to_tkconsole(stats_request.message)
                    logging.info(stats_request.message)

        print(self.playerList)

        # Prepare outputs
        axis_team = []
        allies_team = []

        if self.playerList:
            for item in self.playerList:
                if (
                    str(item.faction) == str(Faction.US)
                    or str(item.faction) == str(Faction.CW)
                ):
                    if item.name != "":
                        allies_team.append(item)
                if (
                    str(item.faction) == str(Faction.WM)
                    or str(item.faction) == str(Faction.PE)
                ):
                    if item.name != "":
                        axis_team.append(item)
        else:
            # To players to process
            return False

        # output each player to file
        if (self.settings.data.get('enable_overlay')):
            self.save_overlay_HTML(axis_team, allies_team)

        # Create text output according to 
        # twitch text preformat string
        if (int(self.numberOfComputers) > 0):
            self.ircStringOutputList.append(
                "Game with " + str(self.numberOfComputers) +
                " computer AI, (" + str(self.easyCPUCount) +
                ") Easy, (" + str(self.normalCPUCount) +
                ") Normal, (" + str(self.hardCPUCount) +
                ") Hard, (" + str(self.expertCPUCount) +
                ") Expert."
            )



        for item in self.playerList:
            # check if item has stats if not it is a computer

            if item.stats:

                steamNumber = self.settings.data.get('steamNumber')
                if (str(item.stats.steamNumber) == str(steamNumber)):
                    if (self.settings.data.get('showOwn')):
                        self.ircStringOutputList = (
                            self.ircStringOutputList +
                            self.create_custom_output(item))
                        
                else:
                    self.ircStringOutputList = (
                        self.ircStringOutputList +
                        self.create_custom_output(item))

        for item in self.ircStringOutputList:
            # outputs the information to IRC
            if self.irc_client:
                self.irc_client.send_private_message_to_IRC(str(item))
            # outputs to the tk console
            if self.tkconsole:
                self.send_to_tkconsole(str(item))

        # Everything succeeded
        return True

    def create_custom_output(self, player) -> list:
        stringFormattingDictionary = (
            self.populate_string_formatting_dictionary(player)
        )
        customPreFormattedOutputString = (
            self.settings.data.get('chat_custom_pf')
        )
        theString = (
            self.format_preformatted_string(
                customPreFormattedOutputString,
                stringFormattingDictionary)
        )
        outputList = list(self.split_by_n(theString, 500))

        return outputList

    def populate_string_formatting_dictionary(self,
                                              player,
                                              overlay=False,
                                              match_type = None):
        if not match_type:
            match_type = self.matchType
        prefixDiv = ""
        postfixDivClose = ""
        if overlay:
            prefixDiv = '<div class = "textVariables">'
            postfixDivClose = '</div>'
        stringFormattingDictionary = dict(
            self.settings.stringFormattingDictionary)
        # loads default values from parameters into
        # stringFormattingDictionary (Key: Value:None)
        nameDiv = ""
        factionDiv = ""
        matchDiv = ""
        countryDiv = ""
        totalWinsDiv = ""
        totalLossesDiv = ""
        totalWinLossRatioDiv = ""
        winsDiv = ""
        lossesDiv = ""
        disputesDiv = ""
        streakDiv = ""
        dropsDiv = ""
        rankDiv = ""
        levelDiv = ""
        wlRatioDiv = ""
        steamprofile = ""
        cohstatslink = ""
        steamid = ""

        if overlay:
            nameDiv = '<div class = "name">'
            factionDiv = '<div class = "faction">'
            matchDiv = '<div class = "matchtype">'
            countryDiv = '<div class = "country">'
            totalWinsDiv = '<div class = "totalwins">'
            totalLossesDiv = '<div class = "totallosses">'
            totalWinLossRatioDiv = '<div class = "totalwlratio">'
            winsDiv = '<div class = "wins">'
            lossesDiv = '<div class = "losses">'
            disputesDiv = '<div class = "disputes">'
            streakDiv = '<div class = "streak">'
            dropsDiv = '<div class = "drops">'
            rankDiv = '<div class = "rank">'
            levelDiv = '<div class = "level">'
            wlRatioDiv = '<div class = "wlratio">'
            steamprofile = '<div class = "steamprofile">'
            cohstatslink = '<div class = "cohstatslink">'
            steamid = '<div class = "steamid">'

        playerName = self.sanatize_user_name(player.name)
        if not playerName:
            playerName = ""
        stringFormattingDictionary['$NAME$'] = (
            prefixDiv + nameDiv + str(playerName) + postfixDivClose +
            postfixDivClose
        )

        if overlay:
            stringFormattingDictionary['$NAME$'] = (
                prefixDiv + nameDiv + str(html.escape(playerName)) +
                postfixDivClose + postfixDivClose
            )

        if type(player.faction) is Faction:
            stringFormattingDictionary['$FACTION$'] = (
                prefixDiv + factionDiv + str(player.faction.name) +
                postfixDivClose + postfixDivClose
            )

        if (match_type == MatchType.CUSTOM):
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + "Basic" + postfixDivClose +
                postfixDivClose
            )

        elif (match_type == MatchType.ONES):
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + "1v1" + postfixDivClose +
                postfixDivClose
            )

        elif (match_type == MatchType.TWOS):
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + "2v2" + postfixDivClose +
                postfixDivClose
            )

        elif (match_type == MatchType.THREES):
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + "3v3" + postfixDivClose +
                postfixDivClose
            )

        elif (match_type == MatchType.FOURS):
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + "4v4" + postfixDivClose +
                postfixDivClose
            )

        else:
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + match_type.name + postfixDivClose +
                postfixDivClose
            )

        # if a computer it will have no stats
        if player.stats:
            stringFormattingDictionary['$COUNTRY$'] = (
                prefixDiv + countryDiv + str(player.stats.country) +
                postfixDivClose + postfixDivClose
            )

            stringFormattingDictionary['$TOTALWINS$'] = (
                prefixDiv + totalWinsDiv + str(player.stats.totalWins) +
                postfixDivClose + postfixDivClose
            )

            stringFormattingDictionary['$TOTALLOSSES$'] = (
                prefixDiv + totalLossesDiv + str(player.stats.totalLosses) +
                postfixDivClose + postfixDivClose
            )

            stringFormattingDictionary['$TOTALWLRATIO$'] = (
                prefixDiv + totalWinLossRatioDiv +
                str(player.stats.totalWLRatio) + postfixDivClose +
                postfixDivClose
            )

            stringFormattingDictionary['$STEAMPROFILE$'] = (
                prefixDiv + steamprofile +
                str(player.stats.steamProfileAddress) +
                postfixDivClose + postfixDivClose
            )

            stringFormattingDictionary['$COHSTATSLINK$'] = (
                prefixDiv + cohstatslink + str(player.stats.cohstatsLink) +
                postfixDivClose + postfixDivClose
            )

            stringFormattingDictionary['$STEAMID$'] = (
                prefixDiv + steamid + str(player.stats.steamNumber) +
                postfixDivClose + postfixDivClose
            )

            # set default null values for all parameters in dictionary
            # these should not be used but are here for reference

            stringFormattingDictionary['$WINS$'] = (
                prefixDiv + winsDiv + "0" + postfixDivClose + postfixDivClose
            )

            stringFormattingDictionary['$LOSSES$'] = (
                prefixDiv + lossesDiv + "0" + postfixDivClose +
                postfixDivClose
            )

            stringFormattingDictionary['$DISPUTES$'] = (
                prefixDiv + disputesDiv + "0" + postfixDivClose +
                postfixDivClose
            )

            stringFormattingDictionary['$STREAK$'] = (
                prefixDiv + streakDiv + "0" + postfixDivClose +
                postfixDivClose
            )

            stringFormattingDictionary['$DROPS$'] = (
                prefixDiv + dropsDiv + "0" + postfixDivClose + postfixDivClose
            )

            stringFormattingDictionary['$RANK$'] = (
                prefixDiv + rankDiv + "" + postfixDivClose + postfixDivClose
            )

            stringFormattingDictionary['$LEVEL$'] = (
                prefixDiv + levelDiv + "0" + postfixDivClose + postfixDivClose
            )

            stringFormattingDictionary['$WLRATIO$'] = (
                prefixDiv + wlRatioDiv + "-" + postfixDivClose +
                postfixDivClose
            )

            # This is where the decision of which values to sub gets made

            for value in player.stats.leaderboardData:
                matchType = str(player.stats.leaderboardData[value].matchType)
                # only show current match type from in game
                if matchType == str(match_type):
                    faction = str(player.stats.leaderboardData[value].faction)
                    # only show current player faction from in game
                    if faction == str(player.faction):
                        stringFormattingDictionary['$WINS$'] = (
                            prefixDiv + winsDiv +
                            str(player.stats.leaderboardData[value].wins) +
                            postfixDivClose + postfixDivClose
                        )

                        stringFormattingDictionary['$LOSSES$'] = (
                            prefixDiv + lossesDiv +
                            str(player.stats.leaderboardData[value].losses) +
                            postfixDivClose + postfixDivClose
                        )

                        stringFormattingDictionary['$DISPUTES$'] = (
                            prefixDiv + disputesDiv +
                            str(player.stats.leaderboardData[value].disputes) +
                            postfixDivClose + postfixDivClose
                        )

                        stringFormattingDictionary['$STREAK$'] = (
                            prefixDiv + streakDiv +
                            str(player.stats.leaderboardData[value].streak) +
                            postfixDivClose + postfixDivClose
                        )

                        stringFormattingDictionary['$DROPS$'] = (
                            prefixDiv + dropsDiv +
                            str(player.stats.leaderboardData[value].drops) +
                            postfixDivClose + postfixDivClose
                        )

                        rank = player.stats.leaderboardData[value].rank
                        if rank == -1:
                            rank = ""
                        stringFormattingDictionary['$RANK$'] = (
                            prefixDiv + rankDiv +
                            str(rank) +
                            postfixDivClose + postfixDivClose
                        )

                        rl = player.stats.leaderboardData[value].rankLevel
                        if rl == -1:
                            rl = "0"
                        stringFormattingDictionary['$LEVEL$'] = (
                            prefixDiv + levelDiv + str(rl) + postfixDivClose +
                            postfixDivClose
                        )

                        wlr = player.stats.leaderboardData[value].winLossRatio
                        stringFormattingDictionary['$WLRATIO$'] = (
                            prefixDiv + wlRatioDiv + str(wlr) +
                            postfixDivClose + postfixDivClose
                        )

        return stringFormattingDictionary

    def populate_image_formatting_dictionary(self,
                                             player,
                                             match_type = None):
        if not match_type:
            match_type = self.matchType
        imageOverlayFDict = (
            self.settings.imageOverlayFormattingDictionary)

        # faction icons
        if player.faction:
            fileExists = False
            factionIcon = ""
            if type(player.faction) is Faction:
                factionIcon = "overlay_images\\armies\\" + str(
                    player.faction.name).lower() + ".png"
                fileExists = os.path.isfile(factionIcon)
            #logging.info(factionIcon)
            if fileExists:
                imageOverlayFDict['$FACTIONICON$'] = (
                    "<div class = 'factionflagimg'>" +
                    f"<img src='{factionIcon}' ></div>"
                )

            else:
                imageOverlayFDict['$FACTIONICON$'] = (
                    '<div class = "factionflagimg">'
                    '<img src="data:," alt></div>'
                )

        # if a computer it will have no stats therefore no country flag or rank
        # set default values for flags and faction rank

        imageOverlayFDict['$FLAGICON$'] = (
            '<div class = "countryflagimg">'
            '<img src="data:," alt></div>'
        )

        defaultFlagIcon = "overlay_images\\flags_small\\unknown_flag.png"
        fileExists = os.path.isfile(defaultFlagIcon)
        if fileExists:
            imageOverlayFDict['$FLAGICON$'] = (
                '<div class = "countryflagimg">'
                '<img src="{0}" ></div>'.format(defaultFlagIcon)
            )

        if player.stats:
            if player.stats.country:
                countryIcon = "overlay_images\\flags_small\\" + str(
                    player.stats.country).lower() + ".png"
                fileExists = os.path.isfile(countryIcon)
                if fileExists:
                    imageOverlayFDict['$FLAGICON$'] = (
                        '<div class = "countryflagimg">'
                        '<img src="{0}" ></div>'.format(countryIcon)
                    )
                else:
                    imageOverlayFDict['$FLAGICON$'] = (
                        '<div class = "countryflagimg">'
                        '<img src="data:," alt></div>'
                    )

            # rank icons
            for value in player.stats.leaderboardData:
                matchType = str(player.stats.leaderboardData[value].matchType)
                if matchType == str(match_type):
                    faction = str(player.stats.leaderboardData[value].faction)
                    if faction == str(player.faction):
                        iconPrefix = ""
                        if str(player.faction) == str(Faction.PE):
                            iconPrefix = "panzer_"
                        if str(player.faction) == str(Faction.CW):
                            iconPrefix = "brit_"
                        if str(player.faction) == str(Faction.US):
                            iconPrefix = "us_"
                        if str(player.faction) == str(Faction.WM):
                            iconPrefix = "heer_"

                        level = str(
                            player.stats.leaderboardData[value].rankLevel
                        ).zfill(2)

                        levelIcon = (
                            "overlay_images\\ranks\\" + iconPrefix + level +
                            ".png"
                        )

                        #logging.info("levelIcon : " + str(levelIcon))
                        fileExists = os.path.isfile(levelIcon)
                        if fileExists:

                            imageOverlayFDict['$LEVELICON$'] = (
                                '<div class = "rankimg">'
                                '<img src="{0}" ></div>'.format(levelIcon)
                            )
                        else:
                            imageOverlayFDict['$LEVELICON$'] = (
                                '<div class = "rankimg">'
                                '<img src="data:," alt></div>'
                            )

                            levelIcon = "overlay_images\\ranks\\no_rank_yet.png"
                            if os.path.isfile(levelIcon):
                                imageOverlayFDict['$LEVELICON$'] = (
                                    '<div class = "rankimg">'
                                    '<img src="{0}" ></div>'.format(levelIcon)
                                )

        return imageOverlayFDict

    def sanatize_user_name(self, userName):
        try:
            if userName:
                userName = str(userName)  # ensure type of string
                userName = userName.lstrip("!")
                # add 1 extra whitespace to username if
                # it starts with . or / using rjust to prevent .
                # and / twitch chat commands causing problems
                if (bool(re.match(r"""^[/\.]""", userName))):
                    userName = str(userName.rjust(len(userName)+1))
                # escape any single quotes
                userName = userName.replace("'", "\'")
                # escape any double quotes
                userName = userName.replace('"', '\"')
            return userName
        except Exception as e:
            #logging.info("In sanitizeUserName username less than 2 chars")
            logging.exception("Exception : " + str(e))

    def format_preformatted_string(
        self,
        theString,
        sfDict,
        overlay=False
    ):

        if overlay:
            prefixDiv = '<div class = "nonVariableText">'
            postfixDiv = '</div>'

            # compile a pattern for all the keys
            pattern = re.compile(
                r'(' + '|'.join(
                    re.escape(key) for key in sfDict.keys()
                    ) + r')'
            )

            #logging.info("pattern " + str(pattern))
            # split the string to include the dictionary keys
            fullSplit = re.split(pattern, theString)

            #logging.info("fullSplit " + str(fullSplit))

            # Then replace the Non key values with the postfix and prefix
            for x in range(len(fullSplit)):
                if not fullSplit[x] in sfDict.keys():
                    fullSplit[x] = prefixDiv + fullSplit[x] + postfixDiv

            # This string can then be processed to replace
            # the keys with their appropriate values

            theString = "".join(fullSplit)

        # I'm dammed if I know how this regular expression works but it does.
        pattern = re.compile(
            r'(?<!\w)(' + '|'.join(
                re.escape(key) for key in sfDict.keys()
                ) + r')(?!\w)'
        )
        result = pattern.sub(
            lambda x: sfDict[x.group()], theString
        )
        return result

    def save_overlay_HTML(self, axisTeamList, alliesTeamList):
        try:
            team1 = ""
            team2 = ""
            team1List = []
            team2List = []

            team1List.clear()
            team2List.clear()

            # by default player team is allies unless
            # the player is steam number is present in the axisTeamList
            team1List = alliesTeamList
            team2List = axisTeamList

            for item in axisTeamList:
                if item.stats:
                    steamNumber = str(self.settings.data.get('steamNumber'))
                    if steamNumber == str(item.stats.steamNumber):
                        # logging.info ("Player team is AXIS")
                        team1List = axisTeamList
                        team2List = alliesTeamList

            uopf = self.settings.data.get('enable_overlay')
            enable_overlay = bool(uopf)
            if (enable_overlay):
                for item in team1List:
                    pf = self.settings.data.get('overlay_default_left_pf')
                    if (self.matchType == MatchType.ONES):
                        pf = self.settings.data.get('overlay_1v1_left_pf')
                    if (self.matchType == MatchType.TWOS):
                        pf = self.settings.data.get('overlay_2v2_left_pf')
                    if (self.matchType == MatchType.THREES):
                        pf = self.settings.data.get('overlay_3v3_left_pf')
                    if (self.matchType == MatchType.FOURS):
                        pf = self.settings.data.get('overlay_4v4_left_pf')
                    if (self.matchType == MatchType.CUSTOM):
                        pf = self.settings.data.get('overlay_custom_left_pf')
                    if (not self.live_game):
                        pf = self.settings.data.get('overlay_default_left_pf')
                    preFormattedString = pf
                    # first substitute all the text in the preformat
                    sfDict = self.populate_string_formatting_dictionary(
                        item,
                        overlay=True
                    )
                    # second substitue all the html images if used
                    sfDict.update(
                        self.populate_image_formatting_dictionary(item))
                    # formats the pf string with html
                    theString = self.format_preformatted_string(
                        preFormattedString,
                        sfDict,
                        overlay=True
                    )
                    theString = f'<div class = "{item.faction.name}">{theString}</div>'
                    team1 += str(theString)

                for item in team2List:
                    pf = self.settings.data.get('overlay_default_right_pf')
                    if (self.matchType == MatchType.ONES):
                        pf = self.settings.data.get('overlay_1v1_right_pf')
                    if (self.matchType == MatchType.TWOS):
                        pf = self.settings.data.get('overlay_2v2_right_pf')
                    if (self.matchType == MatchType.THREES):
                        pf = self.settings.data.get('overlay_3v3_right_pf')
                    if (self.matchType == MatchType.FOURS):
                        pf = self.settings.data.get('overlay_4v4_right_pf')
                    if (self.matchType == MatchType.CUSTOM):
                        pf = self.settings.data.get('overlay_custom_right_pf')
                    if (not self.live_game):
                        pf = self.settings.data.get('overlay_default_right_pf')
                    preFormattedString = pf
                    # first substitute all the text in the preformat
                    sfDict.clear()
                    sfDict = self.populate_string_formatting_dictionary(
                        item,
                        overlay=True
                    )

                    # second substitue all the html images if used
                    sfDict.update(
                        self.populate_image_formatting_dictionary(item)
                    )
                    theString = self.format_preformatted_string(
                        preFormattedString,
                        sfDict,
                        overlay=True
                    )
                    theString = f'<div class = "{item.faction.name}">{theString}</div>'
                    team2 += str(theString)
            else:

                for item in team1List:
                    team1 += str(item.name)
                for item in team2List:
                    team2 += str(item.name)


            if self.automatch:
                cssFilePath = self.settings.data.get('css_style_ranked')
            else:
                cssFilePath = self.settings.data.get('css_style_unranked')

            if (self.matchType == MatchType.CUSTOM or
                self.matchType.value > 8 or
                not self.live_game):
                    cssFilePath = self.settings.data.get('css_style_custom')

            # add match type div surrounding each team
            team1 = f'<div class = "{self.matchType.name}">{team1}</div>'
            team2 = f'<div class = "{self.matchType.name}">{team2}</div>'

            # check if css file exists
            # and if not output the default template to folder
            if cssFilePath:
                if not (os.path.isfile(cssFilePath)):
                    with open(
                        cssFilePath,
                        'w',
                        encoding="utf-8"
                    ) as outfile:
                        outfile.write(OverlayTemplates().overlaycss)

            htmlOutput = OverlayTemplates().overlayhtml.format(
                cssFilePath,
                team1,
                team2
            )
            # create output overlay from template
            with open(
                "overlay.html",
                'w',
                encoding="utf-8"
            ) as outfile:
                outfile.write(htmlOutput)
                # logging.info("Creating Overlay File\n")

        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")

    @staticmethod
    def clear_overlay_HTML():
        try:
            htmlOutput = OverlayTemplates().overlayhtml.format("", "", "")
            # create output overlay from template
            with open("overlay.html", 'w') as outfile:
                outfile.write(htmlOutput)
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")

    def create_stats_html(self, player):
        "Creates stats.html to display player stats in full."
            
        if not player.stats:
            message = "Unable to get data from the relic server."
            self.send_to_tkconsole(message)
            logging.error(message)
            return

        cssFilePath = self.settings.data.get('css_style_display')
        # if the css file doens't exist create one from template
        if cssFilePath:
            if not (os.path.isfile(cssFilePath)):
                with open(
                    cssFilePath,
                    'w',
                    encoding="utf-8"
                ) as outfile:
                    outfile.write(OverlayTemplates().overlaycss)

        pf = self.settings.data.get('overlay_display_pf')
        # first substitute all the text in the preformat

        # loop over all game types
        theString = ""

        display_match_type = -1
        display_match_type = self.settings.data.get('display_match_type')
        try:
            display_match_type = int(display_match_type)
        except ValueError as e:
            logging.error(e)
        display_faction = -1
        display_faction = self.settings.data.get('display_faction')
        try:
            display_faction = int(display_faction)
        except ValueError as e:
            logging.error(e)


        for match in MatchType:
            for faction in Faction:
                for value in player.stats.leaderboardData:
                    ld = player.stats.leaderboardData[value]
                    playerFaction = str(ld.faction)
                    if (playerFaction == str(faction)):
                        playerMatchtype = str(ld.matchType)
                        if (playerMatchtype == str(match)):
                            self.matchType = match
                            player.faction = faction
                            sFD = self.populate_string_formatting_dictionary(player, overlay=True)
                            sFD.update(self.populate_image_formatting_dictionary(player))

                            if display_match_type == match.value or display_match_type == -1:

                                match_type_div = f'<div class = "{match.name}">'

                                if display_faction == faction.value or display_faction == -1:

                                    faction_type_div = f'<div class = "{faction.name}">'

                                    theString += match_type_div
                                    theString += faction_type_div
        
                                    theString += self.format_preformatted_string(pf, sFD, overlay=True)

                                    theString += "</div></div>"

        

        # injects the html output into template
        htmlOutput = OverlayTemplates().statshtml.format(
            cssFilePath,
            theString)
        # create output overlay from template
        with open(
            "stats.html",
            'w',
            encoding="utf-8"
        ) as outfile:
            outfile.write(htmlOutput)


    @staticmethod
    def clear_stats_HTML():
        try:
            htmlOutput = OverlayTemplates().statshtml.format( "", "")
            # create output overlay from template
            with open("stats.html", 'w') as outfile:
                outfile.write(htmlOutput)
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")

    def split_by_n(self, seq, n):
        "A generator to divide a sequence into chunks of n units."
        while seq:
            yield seq[:n]
            seq = seq[n:]

    def find_between(self, s, first, last):
        "Returns the string between two delimiters."

        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def __str__(self):
        output = "GameData : \n"
        output += f"Time Last Game Started : {str(self.gameStartedDate)}\n"
        output += f"player List : {str(self.playerList)}\n"
        output += f"numberOfPlayers : {str(self.numberOfPlayers)}\n"
        output += f"Number Of Computers : {str(self.numberOfComputers)}\n"
        output += f"Easy CPU : {str(self.easyCPUCount)}\n"
        output += f"Normal CPU : {str(self.normalCPUCount)}\n"
        output += f"Hard CPU : {str(self.hardCPUCount)}\n"
        output += f"Expert CPU : {str(self.expertCPUCount)}\n"
        output += f"Number Of Humans : {str(self.numberOfHumans)}\n"
        output += f"Match Type : {str(self.matchType.name)}\n"
        output += f"slots : {str(self.slots)}\n"
        output += f"mapName : {str(self.mapName)}\n"
        output += f"mapNameFull : {str(self.mapNameFull)}\n"
        output += f"mapDescription : {str(self.mapDescription)}\n"
        output += f"mapDescriptionFull : {str(self.mapDescriptionFull)}\n"
        output += f"randomStart : {str(self.randomStart)}\n"
        output += f"highResources : {str(self.highResources)}\n"
        output += f"VPCount : {str(self.VPCount)}\n"
        output += f"automatch : {str(self.automatch)}\n"
        output += f"modName : {str(self.modName)}\n"
        output += f"COH running : {str(self.coh_running)}\n"
        output += f"COH__REC present : {str(self.live_game)}\n"
        output += f"gameStartedDate : {str(self.gameStartedDate)}\n"
        output += (
            f"gameDescriptionString : "
            f"{str(self.gameDescriptionString)}\n"
        )

        return output

    def __repr__(self):
        return str(self)
