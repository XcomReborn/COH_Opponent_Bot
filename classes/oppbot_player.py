from classes.oppbot_faction import Faction
from classes.oppbot_player_stat import PlayerStat


class Player:
    "COH1 player, name and faction can be CPU, humans link to stats."

    def __init__(self,
                name = None,
                faction_name = None,
                team = None,
                player_type = None,
                faction : Faction = None):
        self.name = name
        self.faction_name = faction_name
        self.faction = faction
        self.team = team # 0, 1
        self.player_type = player_type # 0, 1, 2, 5 - human, AI, remote human, empty slot
        self.player_type_name = None # "human", "computer", "remote human", "empty slot"
        self.is_human = False
        self.is_computer = False
        self.is_remote_human = False
        self.is_empty_slot = False
        self.stats : PlayerStat = None
        # This will be None for computers
        # but point to a playerStat Object for players

        if self.faction_name == "axis":
            self.faction = Faction.WM
        if self.faction_name == "allies":
            self.faction = Faction.US
        if self.faction_name == "allies_commonwealth":
            self.faction = Faction.CW
        if self.faction_name == "axis_panzer_elite":
            self.faction = Faction.PE

        if self.player_type == 0:
            self.player_type_name = "human"
            self.is_human = True
        elif self.player_type == 1:
            self.player_type_name = "computer"
            self.is_computer = True
        elif self.player_type == 2:
            self.player_type_name = "remote human"
            self.is_remote_human = True
        elif self.player_type == 5:
            self.player_type_name = "empty slot"
            self.is_empty_slot = True

    def __str__(self):
        output = f"name : {self.name}\n"
        output += f"faction_name : {self.faction_name}\n"
        output += f"faction : {self.faction}\n"
        output += f"team : {self.team}\n"
        output += f"player_type : {self.player_type}\n" 
        output += f"player_type_name : {self.player_type_name}\n"
        output += f"is_human : {self.is_human}\n"
        output += f"is_computer : {self.is_computer}\n"
        output += f"is_remote_human : {self.is_remote_human}\n"
        output += f"is_empty_slot : {self.is_empty_slot}\n"
        output += f"stats : {self.stats}\n"
        return output   

    def __repr__(self):
        return str(self)
