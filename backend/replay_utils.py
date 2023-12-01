from enum import Enum

baseUrl = "https://pokemonshowdown.com/"
replayBaseUrl = "https://replay.pokemonshowdown.com/"
ladderUrl = baseUrl + "ladder/"

class Tier(Enum):
    OU = 'ou'
    UU = 'uu'
    RU = 'ru'
    NU = 'nu'
    PU = 'pu'
    ZU = 'zu'
    NFE = 'nfe'
    LC = 'lc'
    CAP = 'cap'
    Ubers = 'ubers'
    AnythingGoes = 'anythinggoes'
    OneVOne = '1v1'
    Monotype = 'monotype'

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