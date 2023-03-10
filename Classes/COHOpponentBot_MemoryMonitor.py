import logging
import threading
from Classes.COHOpponentBot_Faction import Faction

from Classes.COHOpponentBot_Settings import Settings
from Classes.COHOpponentBot_GameData import GameData
from Classes.COHOpponentBot_IRC_Client import IRC_Client
from Classes.COHOpponentBot_StatsRequest import StatsRequest


class MemoryMonitor(threading.Thread):
    """Checks when COH1 game has started/ended."""

    def __init__(
        self,
        pollInterval=10,
        ircClient: IRC_Client = None,
        settings=None
                ):
        threading.Thread.__init__(self)
        try:
            logging.info("Memory Monitor Started!")
            self.running = True

            self.settings = settings
            if not settings:
                self.settings = Settings()

            self.pm = None
            self.baseAddress = None
            self.gameInProgress = False

            self.ircClient = ircClient
            self.pollInterval = int(pollInterval)
            self.event = threading.Event()
            self.gameData = None
            self.winLostTimer = None

        except Exception as e:
            logging.error("In FileMonitor __init__")
            logging.error(str(e))
            logging.exception("Exception : ")

    def run(self):
        try:
            while self.running:
                self.get_gamedata()
                if self.gameInProgress:

                    if self.gameData.gameInProgress != self.gameInProgress:
                        # coh was running and now its not (game over)
                        self.game_over()
                else:
                    if self.gameData.gameInProgress != self.gameInProgress:
                        # coh wasn't running and now it is (game started)
                        self.game_started()

                # set local gameInProgress flag to it can be compared with
                # any changes to it in the next loop
                self.gameInProgress = self.gameData.gameInProgress
                self.event.wait(self.pollInterval)
        except Exception as e:
            logging.error("In FileMonitor run")
            logging.error(str(e))
            logging.exception("Exception : ")

    def get_gamedata(self):
        try:
            self.gameData = GameData(
                ircClient=self.ircClient,
                settings=self.settings)
            self.gameData.get_data_from_game()
        except Exception as e:
            logging.error("In getGameData")
            logging.info(str(e))
            logging.exception("Exception : ")

    def game_started(self):
        try:
            self.gameData.output_opponent_data()
            # legacy posting of data to opponent bot channel
            self.post_steam_number()
            # enable to output to the opponent bot channel
            self.post_data()
            # enable to output to the opponent bot channel
            self.start_bets()
            # enable to set odds
            self.set_odds()

        except Exception as e:
            logging.info("Problem in GameStarted")
            logging.error(str(e))
            logging.exception("Exception : ")

    def post_steam_number(self):
        try:
            channel = str(self.settings.data.get('channel'))
            steamNumber = str(self.settings.data.get('steamNumber'))
            message = f"!setsteam,{channel},{steamNumber}"
            self.ircClient.send_message_to_opponentbot_channel(message)
        except Exception as e:
            logging.error("Problem in PostSteamNumber")
            logging.exception("Exception : ")
            logging.error(str(e))

    def post_data(self):
        # Sending to cohopponentbot channel about game,
        # this requires parsing mapName First
        try:
            message = self.gameData.get_game_description_string()
            if message:
                self.ircClient.send_message_to_opponentbot_channel(message)

        except Exception as e:
            logging.error("Problem in PostData")
            logging.error(str(e))
            logging.exception("Exception : ")

    def game_over(self):
        try:
            # Get Win/Lose from server after 50 seconds
            # legacy can only be turned on by toggle in file
            # removed from GUI because server win / lose inconsistant
            # occasionally reports incorrectly therefore not worth using.
            # by default writeIWonLostInChat now set to False in file.
            if self.settings.data.get('writeIWonLostInChat'):
                self.winLostTimer = threading.Timer(50.0, self.get_win_lose)
                self.winLostTimer.start()
            # Clear the overlay
            if (self.settings.data.get('clearOverlayAfterGameOver')):
                self.ircClient.queue.put("CLEAROVERLAY")
        except Exception as e:
            logging.info("Problem in GameOver")
            logging.error(str(e))
            logging.exception("Exception : ")

    def get_win_lose(self):
        try:
            # legacy method for info only
            # match history doesn't always get updated immediately.
            # unknown delay or faulty server means can report incorrectly.
            # therefore not used, code kept for reference only.
            statnumber = self.settings.data.get('steamNumber')
            statRequest = StatsRequest(settings=self.settings)
            statRequest.get_match_history_from_server(statnumber)
            mostRecentWin = statRequest.get_player_win_last_match(statnumber)
            if mostRecentWin:
                self.ircClient.send_private_message_to_IRC("!I won")
            else:
                self.ircClient.send_private_message_to_IRC("!I lost")

        except Exception as e:
            logging.info("Problem in GetWinLose")
            logging.error(str(e))
            logging.exception("Exception : ")

    def start_bets(self):

        info = (
            f"Size of self.gameData.playerList "
            f"in StartBets {len(self.gameData.playerList)}"
        )
        logging.info(info)
        if (bool(self.settings.data.get('writePlaceYourBetsInChat'))):
            ps = ""
            outputList = []
            if self.gameData:
                if self.gameData.playerList:
                    if len(self.gameData.playerList) == 2:
                        # if two player make sure the streamer is put first
                        for player in self.gameData.playerList:
                            output = player.name
                            output += " "
                            output += player.faction.name
                            outputList.append(output)
                        # player list does not have steam numbers.
                        # Need to aquire these from warning.log
                        ps = f"{outputList[1]} Vs. {outputList[0]}"
                        pls = self.gameData.playerList[0].stats
                        if pls:
                            sn = str(self.settings.data.get('steamNumber'))
                            psn = str(pls.steamNumber)
                            if sn == psn:
                                ps = f"{outputList[0]} Vs. {outputList[1]}"

                    message = "!startbets {}".format(ps)
                    self.ircClient.send_private_message_to_IRC(message)

    def set_odds(self):
        if (bool(self.settings.data.get('automaticSetBettingOdds'))):
            if self.gameData:
                if self.gameData.playerList:
                    odds = 0.5
                    contenderTeamRatio = 0
                    opponentTeamRatio = 0
                    axisTeamList = []
                    alliesTeamList = []

                    for item in self.gameData.playerList:
                        if (
                            str(item.faction) == str(Faction.US)
                            or str(item.faction) == str(Faction.CW)
                        ):
                            if item.name != "":
                                alliesTeamList.append(item)
                        if (
                            str(item.faction) == str(Faction.WM)
                            or str(item.faction) == str(Faction.PE)
                        ):
                            if item.name != "":
                                axisTeamList.append(item)

                    team1List = []
                    team2List = []

                    # by default player team is allies unless
                    # the player is steam number is present in
                    # the axisTeamList
                    team1List = alliesTeamList
                    team2List = axisTeamList

                    for item in axisTeamList:
                        if item.stats:
                            steamNumber = str(
                                self.settings.data.get('steamNumber'))
                            if steamNumber == str(
                                    item.stats.steamNumber):
                                # logging.info ("Player team is AXIS")
                                team1List = axisTeamList
                                team2List = alliesTeamList
                    # The contender is now in team1List
                    for player in team1List:
                        for value in player.stats.leaderboardData:
                            matchType = str(
                                player.stats.leaderboardData[value].matchType)
                            if matchType == str(self.gameData.matchType):
                                faction = str(
                                    player.stats.leaderboardData[
                                        value].faction)
                                if faction == str(player.faction):
                                    contenderTeamRatio += (
                                        player.stats.leaderboardData[
                                            value].winLossRatio)

                    for player in team2List:
                        for value in player.stats.leaderboardData:
                            matchType = str(
                                player.stats.leaderboardData[value].matchType)
                            if matchType == str(self.gameData.matchType):
                                faction = str(
                                    player.stats.leaderboardData[
                                        value].faction)
                                if faction == str(player.faction):
                                    opponentTeamRatio += (
                                        player.stats.leaderboardData[
                                            value].winLossRatio)

                    try:
                        if opponentTeamRatio:
                            odds = (contenderTeamRatio / (
                                contenderTeamRatio + opponentTeamRatio))
                        else:
                            odds = 0.5
                    except Exception as e:
                        odds = 0.5
                        logging.error(str(e))
                        logging.exception("Exception : ")
                    message = f"!setodds {str(round(odds, 2))}"
                    self.ircClient.send_private_message_to_IRC(message)

    def close(self):
        logging.info("Memory Monitor Closing!")
        self.running = False
        # break out of loops if waiting
        if self.event:
            self.event.set()
        # if timer is running and program is closed then cancel the timer
        # and call getwinlose early. legacy timer.
        if self.winLostTimer:
            self.winLostTimer.cancel()
            # self.GetWinLose()

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""
