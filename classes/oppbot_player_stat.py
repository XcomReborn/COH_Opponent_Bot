import logging
from classes.oppbot_faction import Faction
from classes.oppbot_faction_result import FactionResult
from classes.oppbot_match_type import MatchType


class PlayerStat:
    "Human player stats."

    def __init__(self, statdata = None,
                availableLeaderboards = None,
                steamNumber = None):

        # steamNumber is required in addition to statData
        # to compare the steamNumber to the internal profiles
        # that can contain other profile info

        if not statdata:
            return
        
        if not availableLeaderboards:
            return
        
        if not steamNumber:
            return

        self.leaderboardData = {}
        self.totalWins = 0
        self.totalLosses = 0
        self.totalWLRatio = None
        self.steamNumber = steamNumber
        self.profile_id = None
        self.alias = None
        self.country = None
        self.steamString = None
        self.steamProfileAddress = None
        self.cohstatsLink = None

        statString = "/steam/"+str(steamNumber)


        result = statdata.get('result')
        message = result.get('message')
        if (message == "SUCCESS"):
            for item in statdata.get('statGroups'):
                for value in item.get('members'):
                    if (value.get('name') == statString):
                        self.profile_id = value.get('profile_id')
                        self.alias = value.get('alias')
                        self.steamString = value.get('name')
                        self.country = value.get('country')
        else:
            return

        leaderboards = availableLeaderboards.get('leaderboards')
        leaderboardStats = statdata.get('leaderboardStats')

        for index, stat in enumerate(leaderboardStats):
            leaderboard_id = stat.get('leaderboard_id')

            leaderboard = leaderboards[leaderboard_id]

            name = leaderboard.get('name')
            isranked = leaderboard.get('isranked')
            lbm = leaderboard.get('leaderboardmap')
            match_type = MatchType(lbm[0].get('matchtype_id'))
            faction = Faction(lbm[0].get('race_id'))
            # make leaderboard
            self.leaderboardData[index] = (
            FactionResult(

                faction=faction,
                matchType=match_type,
                name=name,
                leaderboard_id=stat.get(
                    'leaderboard_id'),
                wins=stat.get('wins'),
                losses=stat.get('losses'),
                streak=stat.get('streak'),
                disputes=stat.get('disputes'),
                drops=stat.get('drops'),
                rank=stat.get('rank'),
                rankLevel=stat.get('ranklevel'),
                lastMatch=stat.get('lastMatchDate')
            )
            )

        for leaderboard_id in self.leaderboardData:

            try:
                self.totalWins += int(self.leaderboardData[leaderboard_id].wins)
            except Exception as e:
                logging.error(str(e))
            try:
                self.totalLosses += int(self.leaderboardData[leaderboard_id].losses)
            except Exception as e:
                logging.error(str(e))

        try:
            if (int(self.totalLosses) > 0):
                self.totalWLRatio = str(round(
                    int(self.totalWins)/int(self.totalLosses), 2))

        except Exception as e:
            logging.error("In cohStat creating totalWLRatio")
            logging.error(str(e))
            logging.exception("Exception : ")

        if self.steamString:
            self.steamNumber = str(self.steamString).replace("/steam/", "")
            self.steamProfileAddress = (
                f"steamcommunity.com/profiles/{str(self.steamNumber)}")
            self.cohstatsLink = (
                f"cohstats.com/i?d={str(self.steamNumber)}"
            )

    def __str__(self):

        output = ""
        for value in self.leaderboardData:
            output += str(self.leaderboardData[value])

        output += f"steamNumber : {str(self.steamNumber)}\n"
        output += f"profile_id : {str(self.profile_id)}\n"
        output += f"alias : {str(self.alias)}\n"
        output += f"country : {str(self.country)}\n"
        output += f"steamString : {str(self.steamString)}\n"
        output += f"steamProfileAddress : {str(self.steamProfileAddress)}\n"
        output += f"cohstatsLink : {str(self.cohstatsLink)}\n"
        output += "Totals\n"
        output += f"Wins : {str(self.totalWins)}\n"
        output += f"Losses : {str(self.totalLosses)}\n"
        output += f"W/L Ratio : {str(self.totalWLRatio)}\n"

        return output
