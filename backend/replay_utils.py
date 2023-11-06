from enum import Enum

baseUrl = "https://pokemonshowdown.com/"
replayBaseUrl = "https://replay.pokemonshowdown.com/"
ladderUrl = baseUrl + "ladder/"

class Tier(Enum):
    OU = 1
    UU = 2
    RU = 3
    NU = 4
    PU = 5
    ZU = 6
    NFE = 7
    LC = 8
    CAP = 9
    Ubers = 11
    AnythingGoes = 12
    OneVOne = 13
    Monotype = 14

    def ToString(self):

        #Need to special case 1v1 because it's the only tier with a number in it
        if self == Tier.OneVOne: return "1v1"

        return self.name.lower()

class Generation(Enum):
    I = 1
    II = 2
    III = 3
    IV = 4
    V = 5
    VI = 6
    VII = 7
    VIII = 8
    IX = 9

    def ToString(self):
        return "gen" + str(self.value)


def GetGenerationTierCombo(gen, tier):
    return Generation(gen).ToString() + Tier(tier).ToString()