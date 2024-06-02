import logging
from classes.oppbot_faction import Faction
from classes.oppbot_faction_result import FactionResult
from classes.oppbot_match_type import MatchType


class PlayerStat:
    "Human player stats."

    def __init__(self, statdata, availableLeaderboards, steamNumber):

        # steamNumber is required in addition to statData
        # to compare the steamNumber to the internal profiles
        # that can contain other profile info

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

        if statdata:
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
                if statdata.get('leaderboardStats'):

                    for item in statdata.get('leaderboardStats'):
                        item_leaderboard_id = item.get('leaderboard_id')
                        if item_leaderboard_id:
                            leaderboards = availableLeaderboards.get(
                                'leaderboards'
                            )
                            leaderboard = None
                            for index in leaderboards:
                                if index.get('id') == item_leaderboard_id:
                                    try:
                                        leaderboard = (
                                            leaderboards[item_leaderboard_id])
                                    except Exception as e:
                                        logging.error(str(e))
                                    break

                            if leaderboard:
                                faction = None
                                matchType = None
                                lboardmap = leaderboard.get(
                                    'leaderboardmap')
                                if lboardmap:
                                    try:
                                        faction = Faction(lboardmap[0].get(
                                            'race_id'))
                                        matchType = MatchType(lboardmap[0].get(
                                            'matchtype_id'))
                                    except Exception as e:
                                        logging.error(str(e))

                                self.leaderboardData[leaderboard.get('id')] = (
                                    FactionResult(

                                        faction=faction,
                                        matchType=matchType,
                                        name=leaderboard.get('name'),
                                        leaderboard_id=item.get(
                                            'leaderboard_id'),
                                        wins=item.get('wins'),
                                        losses=item.get('losses'),
                                        streak=item.get('streak'),
                                        disputes=item.get('disputes'),
                                        drops=item.get('drops'),
                                        rank=item.get('rank'),
                                        rankLevel=item.get('ranklevel'),
                                        lastMatch=item.get('lastMatchDate')
                                    )
                                )

        for id in self.leaderboardData:

            try:
                self.totalWins += int(self.leaderboardData[id].wins)
            except Exception as e:
                logging.error(str(e))
            try:
                self.totalLosses += int(self.leaderboardData[id].losses)
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
                f"playercard.cohstats.com/?steamid={str(self.steamNumber)}"
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
