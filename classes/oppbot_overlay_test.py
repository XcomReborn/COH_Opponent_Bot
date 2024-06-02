import tkinter
import webbrowser

from classes.oppbot_faction import Faction
from classes.oppbot_game_data import GameData
from classes.oppbot_match_type import MatchType
from classes.oppbot_player import Player
from classes.oppbot_stats_request import StatsRequest


class OverlayTest:
    
    def __init__(self, settings = None) -> None:
        self.settings = settings

    def create_players(self, numberOfPlayers = 8) -> Player:
        playerList = []

        stats_request = StatsRequest()
        stat = stats_request.return_stats(
            self.settings.data.get('stat_request_number'))

        player_1 = Player()
        player_1.name = "Test Player 1"
        player_1.faction = Faction.US
        if stat:
            player_1.stats = stat
        playerList.append(player_1)

        player_2 = Player()
        player_2.name = "Test Player 2"
        player_2.faction = Faction.WM
        if stat:
            player_2.stats = stat
        playerList.append(player_2)

        player_3 = Player()
        player_3.name = "Test Player 3"
        player_3.faction = Faction.CW
        if stat:
            player_3.stats = stat
        playerList.append(player_3)

        player_4 = Player()
        player_4.name = "Test Player 4"
        player_4.faction = Faction.PE
        if stat:
            player_4.stats = stat
        playerList.append(player_4)

        player_5 = Player()
        player_5.name = "Test Player 5"
        player_5.faction = Faction.US
        if stat:
            player_5.stats = stat
        playerList.append(player_5)

        player_6 = Player()
        player_6.name = "Test Player 6"
        player_6.faction = Faction.WM
        if stat:
            player_6.stats = stat
        playerList.append(player_6)

        player_7 = Player()
        player_7.name = "Test Player 7"
        player_7.faction = Faction.CW
        if stat:
            player_7.stats = stat
        playerList.append(player_7)

        player_8 = Player()
        player_8.name = "Test Player 8"
        player_8.faction = Faction.PE
        if stat:
            player_8.stats = stat
        playerList.append(player_8)

        return playerList[:numberOfPlayers]

    def test_default(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.FOURS
        gamedata.automatch = False
        # create a player object based on steamnumber
        playerList = self.create_players(numberOfPlayers=8)
        gamedata.playerList = playerList
        
        gamedata.output_opponent_data()

    def test_1v1(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.ONES
        gamedata.automatch = True

        # create a player object based on steamnumber
        playerList = self.create_players(numberOfPlayers=2)
        gamedata.playerList = playerList

        gamedata.output_opponent_data()

    def test_2v2(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.TWOS
        gamedata.automatch = True
        # create a player object based on steamnumber
        playerList = self.create_players(numberOfPlayers=4)
        gamedata.playerList = playerList

        gamedata.output_opponent_data()

    def test_3v3(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.THREES
        gamedata.automatch = True
        # create a player object based on steamnumber
        playerList = self.create_players(numberOfPlayers=6)
        gamedata.playerList = playerList

        gamedata.output_opponent_data()

    def test_4v4(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.FOURS
        gamedata.automatch = True
        # create a player object based on steamnumber
        playerList = self.create_players(numberOfPlayers=8)
        gamedata.playerList = playerList

        gamedata.output_opponent_data()

    def test_custom(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.CUSTOM
        gamedata.automatch = False
        # create a player object based on steamnumber
        playerList = self.create_players(numberOfPlayers=8)
        gamedata.playerList = playerList

        gamedata.output_opponent_data()
