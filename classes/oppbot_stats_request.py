import json
import logging
import os
import ssl
import urllib

from classes.oppbot_leaderboard_data import LeaderboardData
from classes.oppbot_settings import Settings
from classes.oppbot_player_stat import PlayerStat


class StatsRequest:
    "Contacts Relic COH1 server via proxy to get steam player data."

    def __init__(self, settings=None):
        self.settings = settings
        if not settings:
            self.settings = Settings()

        # Declare instance variables for storing data
        # returned from server (nested List/Dictionary)
        self.userStatCache = None
        self.availableLeaderboards = None
        self.info = None
        self.message = None
        self.reason = None

    def return_stats(self, steam64ID) -> PlayerStat:
        try:
            self.get_user_stat_from_server(steam64ID)
            # get leaderboard data from class
            lbd = LeaderboardData()
            self.availableLeaderboards = lbd.leaderboard
            # Determine server response succeeded
            # and use it to create PlayerStat object
            result = None
            if self.userStatCache:
                result = self.userStatCache.get('result')
                self.info = self.userStatCache.get('info')
                self.message = self.userStatCache.get('message')
                self.reason = self.userStatCache.get('reason')
            if result:
                if (result.get('message') == "SUCCESS"):
                    result = self.availableLeaderboards.get('result')
                    if result:
                        if result.get('message') == "SUCCESS":
                            playerStat = PlayerStat(
                                self.userStatCache,
                                self.availableLeaderboards,
                                steam64ID)
                            return playerStat
        except Exception as e:
            logging.error("Problem in returnStats")
            logging.error(str(e))
            logging.exception("Exception : ")

    def get_user_stat_from_server(self, steam64ID):
        "Cache the user stats."

        try:
            # check stat number is 17 digit
            # and can be converted to int if not int
            steam64ID = str(steam64ID)
            stringLength = len(steam64ID)
            assert(stringLength == 17)
            assert(int(steam64ID))

            if not os.environ.get('PYTHONHTTPSVERIFY', ''):
                if getattr(ssl, '_create_unverified_context', None):
                    context = ssl._create_unverified_context
                    ssl._create_default_https_context = context

            pd = self.settings.privatedata
            rs = pd.get('relicServerProxyStatRequest')
            rs += str(steam64ID)
            rs += f"&steamNumber={self.settings.data.get('steamNumber')}"
            rs += f"&version={self.settings.privatedata.get('version_number')}"
            response = urllib.request.urlopen(rs).read()
            # Decode server response as a json into a
            # nested list/directory and store as instance variable
            if response:
                try:
                    self.userStatCache = json.loads(response.decode('utf-8'))
                except ValueError as e:
                    logging.error(e)
                except TypeError as e:
                    logging.error(e)

        except Exception as e:
            logging.error("Problem in returnStats")
            logging.error(str(e))
            logging.exception("Exception : ")

    def get_available_leaderboards_from_server(self) -> bool:
        "Cache the available leaderboards. Deprecated"

        try:
            if not os.environ.get('PYTHONHTTPSVERIFY', ''):
                if getattr(ssl, '_create_unverified_context', None):
                    context = ssl._create_unverified_context
                    ssl._create_default_https_context = context

            pd = self.settings.privatedata
            rs = pd.get('relicServerProxyLeaderBoards')
            rs += f"&steamNumber={self.settings.data.get('steamNumber')}"
            rs += f"&version={self.settings.privatedata.get('version_number')}"
            response = urllib.request.urlopen(rs).read()
            #print(response)
            # Decode server response as a json into
            # a nested list/directory and store as instance variable
            if response:
                try:
                    self.availableLeaderboards = json.loads(response.decode('utf-8'))
                    if (self.availableLeaderboards['result']['message'] == "SUCCESS"):
                        return True
                except ValueError as e:
                    logging.error(e)
                except TypeError as e:
                    logging.error(e)

        except Exception as e:
            logging.error("Problem in getMatchHistory")
            logging.error(str(e))
            logging.exception("Exception : ")

    def get_available_leaderboards_from_file(self):
        "load the available leaderboards from file. Deprecated."
        with open('data/available_leaderboards.json', encoding='utf-8') as f:
            self.availableLeaderboards = json.load(f)

    def __str__(self) -> str:
        output = ""
        output += "User Stat Cache : \n"
        uc = self.userStatCache
        output += json.dumps(uc, indent=4, sort_keys=True)
        return output
