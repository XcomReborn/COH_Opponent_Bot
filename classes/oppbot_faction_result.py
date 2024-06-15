import logging
import datetime


class FactionResult():
    "Contains Stat data for each COH1 game type and faction."

    def __init__(
        self, faction=None, matchType=None, name=None, nameShort=None,
        leaderboard_id=None, wins=-1, losses=-1, streak=0,
        disputes=0, drops=0, rank=-1, rankLevel=-1, lastMatch=None
                ):
        self.faction = faction
        self.matchType = matchType
        self.name = name
        self.nameShort = nameShort
        self.id = leaderboard_id
        self.wins = wins
        self.losses = losses
        self.streak = streak
        self.disputes = disputes
        self.drops = drops
        self.rank = rank
        self.rankLevel = rankLevel
        self.lastMatch = lastMatch
        self.lastTime = None
        self.winLossRatio = None

        if isinstance(self.lastMatch, str):
            notNone = (str(self.lastMatch) != "None")
            notEmpty = (str(self.lastMatch) != "")
            if (notNone and notEmpty):
                logging.info("self.lastMatch : %s" , self.lastMatch)
                ts = int(self.lastMatch)
                utc = datetime.utcfromtimestamp(ts)
                self.lastTime = str(utc.strftime('%Y-%m-%d %H:%M:%S'))

        if "American" in self.name:
            self.nameShort = "US"

        if "Wehrmacht" in self.name:
            self.nameShort = "WM"

        if "British" in self.name:
            self.nameShort = "CW"

        if "Panzer" in self.name:
            self.nameShort = "PE"

        if not self.losses:
            self.losses = 0

        if not self.wins:
            self.wins = 0

        try:
            if int(self.losses) != 0:
                wlr = round(int(self.wins)/int(self.losses), 2)
                self.winLossRatio = wlr
            else:
                self.winLossRatio = 1
                if int(self.wins) > 0:
                    self.winLossRatio = "Undefeated"
        except (ValueError,TypeError) as e:
            logging.error("In factionResult Creating winLossRatio")
            logging.error(str(e))
            logging.exception("Exception : ")

    def __str__(self):
        output = "Faction : " + str(self.name) + "\n"
        output += "Faction : " + str(self.faction) + "\n"
        output += "matchType : " + str(self.matchType) + "\n"
        output += "Short Name : " + str(self.nameShort) + "\n"
        output += "Wins : " + str(self.wins) + "\n"
        output += "Losses : " + str(self.losses) + "\n"
        output += "Streak : " + str(self.streak) + "\n"
        output += "Disputes : " + str(self.disputes) + "\n"
        output += "Drops : " + str(self.drops) + "\n"
        output += "Rank : " + str(self.rank) + "\n"
        output += "Level : " + str(self.rankLevel) + "\n"
        output += "Last Time : " + str(self.lastMatch) + "\n"
        output += "winLossRatio : " + str(self.winLossRatio) + "\n"

        return output
