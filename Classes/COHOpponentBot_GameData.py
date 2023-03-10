import ctypes
import datetime
import html
import logging
import os
import re
import time
import pymem
import pymem.process

from mem_edit import Process

from Classes.COHOpponentBot_Faction import Faction
from Classes.COHOpponentBot_MatchType import MatchType
from Classes.COHOpponentBot_Settings import Settings
from Classes.COHOpponentBot_Player import Player
from Classes.COHOpponentBot_ReplayParser import ReplayParser
from Classes.COHOpponentBot_StatsRequest import StatsRequest
from Classes.COHOpponentBot_OverlayTemplates import OverlayTemplates
from Classes.COHOpponentBot_UCS import UCS


class GameData():
    """Contains information about the current COH1 game and players. """

    def __init__(self, ircClient=None, settings=None):
        """Instanciates a new object of type GameData"""

        self.settings = settings
        if not settings:
            self.settings = Settings()

        # Local reference to the IRC client
        self.ircClient = ircClient

        # Pymem handle
        self.pm = None
        self.baseAddress = None
        self.cohProcessID = None

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
        self.cohRunning = False
        self.gameInProgress = False
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

    def clear_data(self):
        """Clears all the variable information in the GameData instance."""

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
        self.cohRunning = False
        self.gameInProgress = False
        self.gameStartedDate = None
        self.cohProcessID = None
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
        """Attempts to get all the COH information from memory."""

        # First Clear all data that can be aquired from the game
        self.clear_data()

        # Check if company of heroes is running if not return false
        if not self.get_COH_memory_address():
            return False

        # Check if a game is currently in progress if not return false.
        # replayParser = self.Get_replayParser_BySearch()
        replayParser = self.get_replayParser_by_search()
        if not replayParser:
            return False

        self.gameStartedDate = replayParser.localDate
        self.randomStart = replayParser.randomStart

        self.highResources = replayParser.highResources
        self.VPCount = replayParser.VPCount
        if replayParser.matchType.lower() == "automatch":
            self.automatch = True
        else:
            self.automatch = False

        self.mapName = replayParser.mapName
        self.mapDescription = replayParser.mapDescription
        self.modName = replayParser.modName

        for item in replayParser.playerList:
            username = item['name']
            factionString = item['faction']
            player = Player(name=username, factionString=factionString)
            self.playerList.append(player)

        statList = self.get_stats_from_game()

        for player in self.playerList:
            if statList:
                for stat in statList:
                    try:
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

        self.numberOfComputers = cpuCounter
        self.numberOfPlayers = cpuCounter + self.numberOfHumans
        self.easyCPUCount = easyCounter
        self.normalCPUCount = normalCounter
        self.hardCPUCount = hardCounter
        self.expertCPUCount = expertCounter

        self.slots = len(replayParser.playerList)

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

        return True

    def get_game_description_string(self) -> str:
        """Produces a single-line game description string."""

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
        """mapDescriptionFull will be None until resolved.

        This takes time because file reading. gets mapDescriptionFull
        from ucs file if they exist there.
        """

        try:
            ucs = UCS(settings=self.settings)
            self.mapDescriptionFull = ucs.compare_UCS(self.mapDescription)

        except Exception as e:
            logging.error("Problem in GetMapDescription")
            logging.exception("Exception : ")
            logging.error(str(e))

    def get_mapNameFull_from_UCS_file(self):
        """mapNameFull will be None until resolved.

        This takes time because file reading
        get mapNameFull from ucs file if they exist there.
        """

        try:
            ucs = UCS(settings=self.settings)
            self.mapNameFull = ucs.compare_UCS(self.mapName)
        except Exception as e:
            logging.error("Problem in GetMapNameFull")
            logging.exception("Exception : ")
            logging.error(str(e))

    def get_pointer_address(self, base: int, offsets: list) -> int | None:
        """Gets memory address from a pointer address (base)
        and applies offsets.

        Parameters
        ----------
        base: int
            The base memory address.

        offsets: list
            The list of offsets.

        Returns
        -------
        int
            The memory address.
        """

        try:
            if self.pm:
                addr = self.pm.read_int(base)
                for i in offsets:
                    if i != offsets[-1]:
                        addr = self.pm.read_int(addr + i)
                return addr + offsets[-1]
        except Exception as e:
            if e:
                return None

    def get_COH_memory_address(self) -> bool:
        """Gets the active process for RelicCOH.exe

        Returns
        -------
        bool
            True if COH is running.
        """

        try:
            self.pm = pymem.Pymem("RelicCOH.exe")
        except Exception as e:
            if e:
                pass
        if self.pm:
            self.cohProcessID = self.pm.process_id
            logging.info(f"self.pm : {str(self.pm)}")
            logging.info(f"cohProcessID : {str(self.cohProcessID)}")
            ph = self.pm.process_handle
            mi = pymem.process.module_from_name(ph, "RelicCOH.exe")
            if mi:
                self.baseAddress = mi.lpBaseOfDll
                info = (
                    "getCOHMemoryAddress self.baseAddress :"
                    f"{str(self.baseAddress)}"
                )
                logging.info(info)
                self.cohRunning = True
                logging.info(f"self.cohRunning {self.cohRunning}")
                return True
        else:
            self.cohRunning = False
            logging.info(f"self.cohRunning {self.cohRunning}")
            return False

    def get_replayParser_by_pointer(self) -> ReplayParser:
        """Gets an instance of the replayParser containing COH game info."""

        # There are four pointers to the replay that appear to be 'static'
        # We can try them in sequence and return the data from the first
        # one that works (Probably the first one)
        myListOfCOHRECPointers = []
        # 1
        cohrecReplayAddress = 0x00902030
        cohrecOffsets = [0x28, 0x160, 0x4, 0x84, 0x2C, 0x110, 0x0]
        myListOfCOHRECPointers.append([cohrecReplayAddress, cohrecOffsets])

        # 2
        cohrecReplayAddress = 0x00902030
        cohrecOffsets = [0x28, 0x160, 0x4, 0x84, 0x24, 0x110, 0x0]
        myListOfCOHRECPointers.append([cohrecReplayAddress, cohrecOffsets])

        # 3
        cohrecReplayAddress = 0x00902030
        cohrecOffsets = [0x4, 0x160, 0x4, 0x118, 0x110, 0x0]
        myListOfCOHRECPointers.append([cohrecReplayAddress, cohrecOffsets])

        # 4
        cohrecReplayAddress = 0x00902030
        cohrecOffsets = [0x4, 0x160, 0x4, 0x110, 0x110, 0x0]
        myListOfCOHRECPointers.append([cohrecReplayAddress, cohrecOffsets])

        for count, item in enumerate(myListOfCOHRECPointers):
            logging.info(f"{count} {item}")
            ad = self.get_pointer_address(self.baseAddress + item[0], item[1])
            actualCOHRECMemoryAddress = ad
            info = (
                f"actualCOHRECMemoryAddress :"
                f"{str(actualCOHRECMemoryAddress)}"
                )
            logging.info(info)
            if actualCOHRECMemoryAddress:
                try:
                    rd = self.pm.read_bytes(actualCOHRECMemoryAddress, 4000)
                except Exception as e:
                    logging.error(e)
                if rd:
                    if rd[4:12] == bytes("COH__REC".encode('ascii')):
                        logging.info("Pointing to COH__REC")
                        self.gameInProgress = True
                        replayByteData = bytearray(rd)
                        replayParser = ReplayParser(parameters=self.settings)
                        replayParser.data = bytearray(replayByteData)
                        logging.info("Successfully Parsed Replay Data")
                        success = replayParser.process_data()
                        if success:
                            return replayParser

        # Sets gameInProgress to False if COH__REC was not found
        # eg game is not in progress.
        self.gameInProgress = False

    def get_replayParser_by_search(self) -> ReplayParser:
        """Gets an instance of the replayParser containing COH game info."""

        if self.pm:
            with Process.open_process(self.pm.process_id) as p:

                searchString = bytearray("COH__REC".encode('ascii'))
                buff = bytes(searchString)

                replayMemoryAddress = p.search_all_memory(buff)

                if replayMemoryAddress:
                    for address in replayMemoryAddress:
                        # There should be only one COH__REC in memory
                        # if the game is running
                        self.gameInProgress = True
                        try:
                            rd = self.pm.read_bytes(address-4, 4000)
                            rd = bytearray(rd)
                            rp = ReplayParser(parameters=self.settings)
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
                else:
                    logging.info("Cannot detect COH__REC in memory.")
                    self.gameInProgress = False

    def get_stats_from_game(self):
        """Provides stats from playerList names from game memory."""

        if self.pm:
            with Process.open_process(self.pm.process_id) as p:
                steamNumberList = []
                steamNumberList.append(self.settings.data.get('steamNumber'))
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
                                    steamNumberList.append(sNumber)
                                    break
                            except Exception as e:
                                if e:
                                    pass

                statList = []
                for item in steamNumberList:
                    statRquest = StatsRequest(settings=self.settings)
                    stat = statRquest.return_stats(item)
                    statList.append(stat)
                return statList

    def test_output(self):
        """Produces text output according to Preformat."""
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
            self.ircClient.send_to_outputfield(output)
            preformat = self.settings.data.get('customStringPreFormat')
            self.ircClient.send_to_outputfield(preformat)

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
            self.ircClient.send_to_outputfield(output)

    def __produceOutput(self, streamerPlayer):
        sFD = self.populate_string_formatting_dictionary(streamerPlayer)
        cPFOS = self.settings.data.get('customStringPreFormat')
        theString = self.format_preformatted_string(cPFOS, sFD)
        outputList = list(self.split_by_n(theString, 500))
        for item in outputList:
            self.ircClient.send_to_outputfield(item)

    def output_opponent_data(self):
        """"Outputs game and player information according to formats."""

        logging.info("In output opponent data")
        logging.info(str(self))

        # Prepare outputs
        axisTeam = []
        alliesTeam = []

        if self.playerList:
            for item in self.playerList:
                if (
                    str(item.faction) == str(Faction.US)
                    or str(item.faction) == str(Faction.CW)
                ):
                    if item.name != "":
                        alliesTeam.append(item)
                if (
                    str(item.faction) == str(Faction.WM)
                    or str(item.faction) == str(Faction.PE)
                ):
                    if item.name != "":
                        axisTeam.append(item)

            # output each player to file
            if (self.settings.data.get('useOverlayPreFormat')):
                self.save_overlay_HTML(axisTeam, alliesTeam)

            # output to chat if customoutput ticked
            if (self.settings.data.get('useCustomPreFormat')):
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
                        if (item.stats.steamNumber == steamNumber):
                            if (self.settings.data.get('showOwn')):
                                self.ircStringOutputList = (
                                    self.ircStringOutputList +
                                    self.create_custom_output(item)
                                )
                        else:
                            self.ircStringOutputList = (
                                self.ircStringOutputList +
                                self.create_custom_output(item)
                            )

                for item in self.ircStringOutputList:
                    self.ircClient.send_private_message_to_IRC(str(item))
                    # outputs the information to IRC

    def create_custom_output(self, player) -> list:
        stringFormattingDictionary = (
            self.populate_string_formatting_dictionary(player)
        )
        customPreFormattedOutputString = (
            self.settings.data.get('customStringPreFormat')
        )
        theString = (
            self.format_preformatted_string(
                customPreFormattedOutputString,
                stringFormattingDictionary)
        )
        outputList = list(self.split_by_n(theString, 500))

        return outputList

    def populate_string_formatting_dictionary(self, player, overlay=False):
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

        if (self.matchType == MatchType.CUSTOM):
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + "Basic" + postfixDivClose +
                postfixDivClose
            )

        if (self.matchType == MatchType.ONES):
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + "1v1" + postfixDivClose +
                postfixDivClose
            )

        if (self.matchType == MatchType.TWOS):
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + "2v2" + postfixDivClose +
                postfixDivClose
            )

        if (self.matchType == MatchType.THREES):
            stringFormattingDictionary['$MATCHTYPE$'] = (
                prefixDiv + matchDiv + "3v3" + postfixDivClose +
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

            for value in player.stats.leaderboardData:
                matchType = str(player.stats.leaderboardData[value].matchType)
                if matchType == str(self.matchType):
                    faction = str(player.stats.leaderboardData[value].faction)
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

    def populate_image_formatting_dictionary(self, player):
        imageOverlayFDict = (
            self.settings.imageOverlayFormattingDictionary)

        # faction icons
        if player.faction:
            fileExists = False
            factionIcon = ""
            if type(player.faction) is Faction:
                factionIcon = "OverlayImages\\Armies\\" + str(
                    player.faction.name).lower() + ".png"
                fileExists = os.path.isfile(factionIcon)
            logging.info(factionIcon)
            if fileExists:
                imageOverlayFDict['$FACTIONICON$'] = (
                    "<div class = 'factionflagimg'>" +
                    f"<img src='{factionIcon}' ></div>"
                )

                logging.info(
                    imageOverlayFDict.get('$FACTIONICON$'))
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

        defaultFlagIcon = "OverlayImages\\Flagssmall\\unknown_flag.png"
        fileExists = os.path.isfile(defaultFlagIcon)
        if fileExists:
            imageOverlayFDict['$FLAGICON$'] = (
                '<div class = "countryflagimg">'
                '<img src="{0}" ></div>'.format(defaultFlagIcon)
            )

        if player.stats:
            if player.stats.country:
                countryIcon = "OverlayImages\\Flagssmall\\" + str(
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
                if matchType == str(self.matchType):
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
                            "OverlayImages\\Ranks\\" + iconPrefix + level +
                            ".png"
                        )

                        logging.info("levelIcon : " + str(levelIcon))
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

                            levelIcon = "OverlayImages\\Ranks\\no_rank_yet.png"
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
            logging.info("In sanitizeUserName username less than 2 chars")
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

            logging.info("pattern " + str(pattern))
            # split the string to include the dictionary keys
            fullSplit = re.split(pattern, theString)

            logging.info("fullSplit " + str(fullSplit))

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

            uopf = self.settings.data.get('useOverlayPreFormat')
            useOverlayPreFormat = bool(uopf)
            if (useOverlayPreFormat):
                for item in team1List:
                    pf = self.settings.data.get('overlayStringPreFormatLeft')
                    preFormattedString = pf
                    # first substitute all the text in the preformat
                    sfDict = self.populate_string_formatting_dictionary(
                        item,
                        overlay=True
                    )
                    # second substitue all the html images if used
                    sfDict.update(
                        self.populate_image_formatting_dictionary(item))
                    theString = self.format_preformatted_string(
                        preFormattedString,
                        sfDict,
                        overlay=True
                    )
                    team1 += str(theString) + str("<BR>") + "\n"
                for item in team2List:
                    preFormattedString = self.settings.data.get(
                        'overlayStringPreFormatRight'
                    )
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
                    team2 += str(theString) + str("<BR>") + "\n"
            else:

                for item in team1List:
                    team1 += str(item.name) + str("<BR>") + "\n"
                for item in team2List:
                    team2 += str(item.name) + str("<BR>") + "\n"

            cssFilePath = self.settings.data.get('overlayStyleCSSFilePath')
            # check if css file exists
            # and if not output the default template to folder
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

    def split_by_n(self, seq, n):
        '''A generator to divide a sequence into chunks of n units.'''
        while seq:
            yield seq[:n]
            seq = seq[n:]

    def find_between(self, s, first, last):
        """Returns the string between two delimiters."""

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
        output += f"COH running : {str(self.cohRunning)}\n"
        output += f"Game In Progress : {str(self.gameInProgress)}\n"
        output += f"gameStartedDate : {str(self.gameStartedDate)}\n"
        output += f"cohProcessID : {str(self.cohProcessID)}\n"
        output += f"baseAddress : {str(self.baseAddress)}\n"
        output += (
            f"gameDescriptionString : "
            f"{str(self.gameDescriptionString)}\n"
        )

        return output

    def __repr__(self):
        return str(self)
