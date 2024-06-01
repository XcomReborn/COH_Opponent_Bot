from enum import Enum


class MatchType(Enum):
    "COH1 MatchTypes Enum"

    CUSTOM = 0
    ONES = 1
    TWOS = 2
    THREES = 3
    FOURS = 4
    TEAM_2V2 = 5
    TEAM_3V3 = 6
    TEAM_4V4 = 7
    ASSAULT_2V2 = 8
    ASSAULT_TEAM_2V2 = 9
    ASSAULT_TEAM_3V3 = 10
    PANZERKRIEG_2v2 = 11
    PANZERKRIEG_TEAM_2v2 = 12
    PANZERKRIEG_TEAM_3v3 = 13
    COMPSTOMP = 14
    ASSAULT = 15
    PANZERKRIEG = 16
    STONEWALL = 17
