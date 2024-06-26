import logging

from classes.oppbot_faction import Faction
from classes.oppbot_game_data import GameData
from classes.oppbot_match_type import MatchType
from classes.oppbot_player import Player
from classes.oppbot_stats_request import StatsRequest


class OverlayTest:
    
    def __init__(self, settings = None, main_window = None) -> None:
        self.settings = settings
        self.main_window = main_window

    def create_players(self, numberOfPlayers = 8) -> Player:
        "creates a number of test players for overlay output."

        stats_request = StatsRequest()
        stat = stats_request.return_stats(
            self.settings.data.get('stat_request_number'))
        if stats_request.info:
            if "DENIED" in stats_request.info:
                message = "Unable to get data from the relic server."
                if self.main_window:
                    self.main_window.send_to_tkconsole(message)
                if stats_request.reason:
                    if self.main_window:
                        self.main_window.send_to_tkconsole(stats_request.reason)
                if stats_request.message:
                    if self.main_window:
                        self.main_window.send_to_tkconsole(stats_request.message)
                logging.error(message)
                return False
            if "OUTOFDATE" in stats_request.info:
                if stats_request.message:
                    if self.main_window:
                        self.main_window.send_to_tkconsole(stats_request.message)
                    logging.info(stats_request.message)

        player_team = []

        player_1 = Player()
        player_1.name = "Test Player 1"
        player_1.faction = Faction.US
        if stat:
            player_1.stats = stat
        player_team.append(player_1)

        player_2 = Player()
        player_2.name = "Test Player 2"
        player_2.faction = Faction.CW
        if stat:
            player_2.stats = stat
        player_team.append(player_2)

        player_3 = Player()
        player_3.name = "Test Player 3"
        player_3.faction = Faction.US
        if stat:
            player_3.stats = stat
        player_team.append(player_3)

        player_4 = Player()
        player_4.name = "Test Player 4"
        player_4.faction = Faction.CW
        if stat:
            player_4.stats = stat
        player_team.append(player_4)

        opponent_team = []

        player_5 = Player()
        player_5.name = "Test Player 5"
        player_5.faction = Faction.WM
        if stat:
            player_5.stats = stat
        opponent_team.append(player_5)

        player_6 = Player()
        player_6.name = "Test Player 6"
        player_6.faction = Faction.PE
        if stat:
            player_6.stats = stat
        opponent_team.append(player_6)

        player_7 = Player()
        player_7.name = "Test Player 7"
        player_7.faction = Faction.WM
        if stat:
            player_7.stats = stat
        opponent_team.append(player_7)

        player_8 = Player()
        player_8.name = "Test Player 8"
        player_8.faction = Faction.PE
        if stat:
            player_8.stats = stat
        opponent_team.append(player_8)

        allies = player_team[:numberOfPlayers//2]
        axis = opponent_team[:numberOfPlayers//2]

        return allies + axis

    def test_default(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.COMPSTOMP
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
        gamedata.live_game = True
        gamedata.output_opponent_data()


    def test_2v2(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.TWOS
        gamedata.automatch = True
        # create a player object based on steamnumber
        playerList = self.create_players(numberOfPlayers=4)
        gamedata.playerList = playerList
        gamedata.live_game = True
        gamedata.output_opponent_data()


    def test_3v3(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.THREES
        gamedata.automatch = True
        # create a player object based on steamnumber
        playerList = self.create_players(numberOfPlayers=6)
        gamedata.playerList = playerList
        gamedata.live_game = True
        gamedata.output_opponent_data()


    def test_4v4(self):
        # create gamedata
        gamedata = GameData(settings=self.settings)
        gamedata.matchType = MatchType.FOURS
        gamedata.automatch = True
        # create a player object based on steamnumber
        playerList = self.create_players(numberOfPlayers=8)
        gamedata.playerList = playerList
        gamedata.live_game = True
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
