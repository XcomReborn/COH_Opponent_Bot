from classes.oppbot_faction import Faction
from classes.oppbot_player_stat import PlayerStat


class Player:
    "COH1 player, name and faction can be CPU, humans link to stats."

    def __init__(self,
                name = None,
                faction_name = None,
                faction : Faction = None):
        self.name = name
        self.faction_name = faction_name
        self.faction = faction
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

    def __str__(self):
        output = f"name : {self.name}\n"
        output += f"faction_name : {self.faction_name}\n"
        output += f"faction : {self.faction}\n"
        output += f"stats : {self.stats}\n"
        return output

    def __repr__(self):
        return str(self)
