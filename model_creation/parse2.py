import logging
import urllib.request
import pandas as pd
from typing import List


def add_action(actions, hash_pkmn, hash_moves, pokemon, boosts, weather, terrain, hazards, moves, user):
    if user == 0:
        i, j = 0, 1
    else:
        i, j = 1, 0
    action_info = {
        'PlayerPkmnOnField': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[i][0][0]])['Number'],
        'PlayerPkmnHealth': pokemon[i][1][0],
        'PlayerPkmnStatus': pokemon[i][2][0],
        'PlayerPkmnType1': pokemon[i][3][0][0],
        'PlayerPkmnType2': pokemon[i][3][0][1],
        'PlayerPkmnHP': pokemon[i][4][0][0],
        'PlayerPkmnAtk': pokemon[i][4][0][1],
        'PlayerPkmnDef': pokemon[i][4][0][2],
        'PlayerPkmnSpA': pokemon[i][4][0][3],
        'PlayerPkmnSpD': pokemon[i][4][0][4],
        'PlayerPkmnSpe': pokemon[i][4][0][5],
        'PlayerBenchOne': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[i][0][1]])['Number'],
        'PlayerBenchOneHp': pokemon[i][1][1],
        'PlayerBenchOneStatus': pokemon[i][2][1],
        'PlayerBenchOneType1': pokemon[i][3][1][0],
        'PlayerBenchOneType2': pokemon[i][3][1][1],
        'PlayerBenchOneHP': pokemon[i][4][1][0],
        'PlayerBenchOneAtk': pokemon[i][4][1][1],
        'PlayerBenchOneDef': pokemon[i][4][1][2],
        'PlayerBenchOneSpA': pokemon[i][4][1][3],
        'PlayerBenchOneSpD': pokemon[i][4][1][4],
        'PlayerBenchOneSpe': pokemon[i][4][1][5],
        'PlayerBenchTwo': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[i][0][2]])['Number'],
        'PlayerBenchTwoHp': pokemon[i][1][2],
        'PlayerBenchTwoStatus': pokemon[i][2][2],
        'PlayerBenchTwoType1': pokemon[i][3][2][0],
        'PlayerBenchTwoType2': pokemon[i][3][2][1],
        'PlayerBenchTwoHP': pokemon[i][4][2][0],
        'PlayerBenchTwoAtk': pokemon[i][4][2][1],
        'PlayerBenchTwoDef': pokemon[i][4][2][2],
        'PlayerBenchTwoSpA': pokemon[i][4][2][3],
        'PlayerBenchTwoSpD': pokemon[i][4][2][4],
        'PlayerBenchTwoSpe': pokemon[i][4][2][5],
        'PlayerBenchThree': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[i][0][3]])['Number'],
        'PlayerBenchThreeHp': pokemon[i][1][3],
        'PlayerBenchThreeStatus': pokemon[i][2][3],
        'PlayerBenchThreeType1': pokemon[i][3][3][0],
        'PlayerBenchThreeType2': pokemon[i][3][3][1],
        'PlayerBenchThreeHP': pokemon[i][4][3][0],
        'PlayerBenchThreeAtk': pokemon[i][4][3][1],
        'PlayerBenchThreeDef': pokemon[i][4][3][2],
        'PlayerBenchThreeSpA': pokemon[i][4][3][3],
        'PlayerBenchThreeSpD': pokemon[i][4][3][4],
        'PlayerBenchThreeSpe': pokemon[i][4][3][5],
        'PlayerBenchFour': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[i][0][4]])['Number'],
        'PlayerBenchFourHp': pokemon[i][1][4],
        'PlayerBenchFourStatus': pokemon[i][2][4],
        'PlayerBenchFourType1': pokemon[i][3][4][0],
        'PlayerBenchFourType2': pokemon[i][3][4][1],
        'PlayerBenchFourHP': pokemon[i][4][4][0],
        'PlayerBenchFourAtk': pokemon[i][4][4][1],
        'PlayerBenchFourDef': pokemon[i][4][4][2],
        'PlayerBenchFourSpA': pokemon[i][4][4][3],
        'PlayerBenchFourSpD': pokemon[i][4][4][4],
        'PlayerBenchFourSpe': pokemon[i][4][4][5],
        'PlayerBenchFive': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[i][0][5]])['Number'],
        'PlayerBenchFiveHp': pokemon[i][1][5],
        'PlayerBenchFiveStatus': pokemon[i][2][5],
        'PlayerBenchFiveType1': pokemon[i][3][5][0],
        'PlayerBenchFiveType2': pokemon[i][3][5][1],
        'PlayerBenchFiveHP': pokemon[i][4][5][0],
        'PlayerBenchFiveAtk': pokemon[i][4][5][1],
        'PlayerBenchFiveDef': pokemon[i][4][5][2],
        'PlayerBenchFiveSpA': pokemon[i][4][5][3],
        'PlayerBenchFiveSpD': pokemon[i][4][5][4],
        'PlayerBenchFiveSpe': pokemon[i][4][5][5],
        'PlayerBoostAtk': boosts[i]["atk"],
        'PlayerBoostDef': boosts[i]["def"],
        'PlayerBoostSpa': boosts[i]["spa"],
        'PlayerBoostSpd': boosts[i]["spd"],
        'PlayerBoostSpe': boosts[i]["spe"],
        'PlayerBoostEva': boosts[i]["evasion"],
        'PlayerBoostAcc': boosts[i]["accuracy"],
        'EnemyPkmnOnField': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[j][0][0]])['Number'],
        'EnemyPkmnHealth': pokemon[j][1][0],
        'EnemyPkmnStatus': pokemon[j][2][0],
        'EnemyPkmnType1': pokemon[j][3][0][0],
        'EnemyPkmnType2': pokemon[j][3][0][1],
        'EnemyPkmnHP': pokemon[j][4][0][0],
        'EnemyPkmnAtk': pokemon[j][4][0][1],
        'EnemyPkmnDef': pokemon[j][4][0][2],
        'EnemyPkmnSpA': pokemon[j][4][0][3],
        'EnemyPkmnSpD': pokemon[j][4][0][4],
        'EnemyPkmnSpe': pokemon[j][4][0][5],
        'EnemyBenchOne': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[j][0][1]])['Number'],
        'EnemyBenchOneHp': pokemon[j][1][1],
        'EnemyBenchOneStatus': pokemon[j][2][1],
        'EnemyBenchOneType1': pokemon[j][3][1][0],
        'EnemyBenchOneType2': pokemon[j][3][1][1],
        'EnemyBenchOneHP': pokemon[j][4][1][0],
        'EnemyBenchOneAtk': pokemon[j][4][1][1],
        'EnemyBenchOneDef': pokemon[j][4][1][2],
        'EnemyBenchOneSpA': pokemon[j][4][1][3],
        'EnemyBenchOneSpD': pokemon[j][4][1][4],
        'EnemyBenchOneSpe': pokemon[j][4][1][5],
        'EnemyBenchTwo': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[j][0][3]])['Number'],
        'EnemyBenchTwoHp': pokemon[j][1][2],
        'EnemyBenchTwoStatus': pokemon[j][2][2],
        'EnemyBenchTwoType1': pokemon[j][3][2][0],
        'EnemyBenchTwoType2': pokemon[j][3][2][1],
        'EnemyBenchTwoHP': pokemon[j][4][2][0],
        'EnemyBenchTwoAtk': pokemon[j][4][2][1],
        'EnemyBenchTwoDef': pokemon[j][4][2][2],
        'EnemyBenchTwoSpA': pokemon[j][4][2][3],
        'EnemyBenchTwoSpD': pokemon[j][4][2][4],
        'EnemyBenchTwoSpe': pokemon[j][4][2][5],
        'EnemyBenchThree': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[j][0][3]])['Number'],
        'EnemyBenchThreeHp': pokemon[j][1][3],
        'EnemyBenchThreeStatus': pokemon[j][2][3],
        'EnemyBenchThreeType1': pokemon[j][3][3][0],
        'EnemyBenchThreeType2': pokemon[j][3][3][1],
        'EnemyBenchThreeHP': pokemon[j][4][3][0],
        'EnemyBenchThreeAtk': pokemon[j][4][3][1],
        'EnemyBenchThreeDef': pokemon[j][4][3][2],
        'EnemyBenchThreeSpA': pokemon[j][4][3][3],
        'EnemyBenchThreeSpD': pokemon[j][4][3][4],
        'EnemyBenchThreeSpe': pokemon[j][4][3][5],
        'EnemyBenchFour': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[j][0][4]])['Number'],
        'EnemyBenchFourHp': pokemon[j][1][4],
        'EnemyBenchFourStatus': pokemon[j][2][4],
        'EnemyBenchFourType1': pokemon[j][3][4][0],
        'EnemyBenchFourType2': pokemon[j][3][4][1],
        'EnemyBenchFourHP': pokemon[j][4][4][0],
        'EnemyBenchFourAtk': pokemon[j][4][4][1],
        'EnemyBenchFourDef': pokemon[j][4][4][2],
        'EnemyBenchFourSpA': pokemon[j][4][4][3],
        'EnemyBenchFourSpD': pokemon[j][4][4][4],
        'EnemyBenchFourSpe': pokemon[j][4][4][5],
        'EnemyBenchFive': (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[j][0][5]])['Number'],
        'EnemyBenchFiveHp': pokemon[j][1][5],
        'EnemyBenchFiveStatus': pokemon[j][2][5],
        'EnemyBenchFiveType1': pokemon[j][3][5][0],
        'EnemyBenchFiveType2': pokemon[j][3][5][1],
        'EnemyBenchFiveHP': pokemon[j][4][5][0],
        'EnemyBenchFiveAtk': pokemon[j][4][5][1],
        'EnemyBenchFiveDef': pokemon[j][4][5][2],
        'EnemyBenchFiveSpA': pokemon[j][4][5][3],
        'EnemyBenchFiveSpD': pokemon[j][4][5][4],
        'EnemyBenchFiveSpe': pokemon[j][4][5][5],
        'EnemyBoostAtk': boosts[j]["atk"],
        'EnemyBoostDef': boosts[j]["def"],
        'EnemyBoostSpa': boosts[j]["spa"],
        'EnemyBoostSpd': boosts[j]["spd"],
        'EnemyBoostSpe': boosts[j]["spe"],
        'EnemyBoostEva': boosts[j]["evasion"],
        'EnemyBoostAcc': boosts[j]["accuracy"],
        'Weather': weather,
        'Terrain': terrain,
        'PlayerStealthRock': hazards[i]['Stealth Rock'],
        'PlayerSpikes': hazards[i]['Spikes'],
        'PlayerToxicSpikes': hazards[i]['Toxic Spikes'],
        'PlayerStickyWeb': hazards[i]['Sticky Web'],
        'PlayerReflect': hazards[i]['Reflect'],
        'PlayerLightScreen': hazards[i]['Light Screen'],
        'PlayerMist': hazards[i]['Mist'],
        'PlayerAuroraVeil': hazards[i]['Aurora Veil'],
        'PlayerSafeguard': hazards[i]['Safeguard'],
        'EnemyStealthRock': hazards[j]['Stealth Rock'],
        'EnemySpikes': hazards[j]['Spikes'],
        'EnemyToxicSpikes': hazards[j]['Toxic Spikes'],
        'EnemyStickyWeb': hazards[j]['Sticky Web'],
        'EnemyReflect': hazards[j]['Reflect'],
        'EnemyLightScreen': hazards[j]['Light Screen'],
        'EnemyMist': hazards[j]['Mist'],
        'EnemyAuroraVeil': hazards[j]['Aurora Veil'],
        'EnemySafeguard': hazards[j]['Safeguard'],
        'PlayerMove': None if moves[i] is None else moves[i] if type(moves[i]) is int else hash_moves[moves[i]],
    }
    actions.append(action_info)


def parse(link, actions, hash_pkmn, hash_moves, count):
    # Represents Pokémon, hp, and status effects
    pokemon = [[[], [100] * 6, [0] * 6], [], [], [[], [100] * 6, [0] * 6], [0] * 6, [], []]
    # Represents base stat changes
    boosts_zero = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0}
    # Represents stat changes
    boosts = [{"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0},
              {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0}]
    # Each Pokémon move
    moves = [None, None]
    weather = 0
    terrain = 0
    hazards = [{'Stealth Rock': 0, 'Spikes': 0, 'Toxic Spikes': 0, 'Sticky Web': 0,
                'Reflect': 0, 'Light Screen': 0, 'Mist': 0, 'Aurora Veil': 0, 'Safeguard': 0},
               {'Stealth Rock': 0, 'Spikes': 0, 'Toxic Spikes': 0, 'Sticky Web': 0,
                'Reflect': 0, 'Light Screen': 0, 'Mist': 0, 'Aurora Veil': 0, 'Safeguard': 0}]

    # current state of Pokémon, boosts, weather, terrain, and statuses
    currPkmn = pokemon
    currBoosts = boosts
    currWeather = weather
    currTerrain = terrain
    currHazards = hazards

    # Create a request object with a User-Agent header
    req = urllib.request.Request(
        link,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.3 '
        }
    )

    try:
        response = urllib.request.urlopen(req)
    except Exception as e:
        logging.exception(e)
        return

    print(str(count) + ':' + link)
    log = response.read().decode('utf-8')
    # Read through each line in the battle log
    for line in log.split('\n'):
        blocks: List[str] = line.split('|')
        if len(blocks) < 2:
            pass
        elif blocks[1] == 'win':
            break
        elif blocks[1] == 'poke':
            i = 0 if blocks[2] == 'p1' else 1
            # pokemon[i][0].append(blocks[3].split(',')[0].split('-*')[0])
            name = blocks[3].split(',')[0].split('-*')[0]
            pkmn_data = hash_pkmn.loc[hash_pkmn['Name'] == name]
            pokemon[i][0].append(name)
            pokemon[i][3].append(pkmn_data[['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe']].values.tolist()[0])
            pokemon[i][4].append(pkmn_data[['Type 1', 'Type 2']].values.tolist()[0])
        elif blocks[1] == 'switch':
            i = 0 if blocks[2].startswith('p1') else 1
            swapIndex = 0
            if blocks[3].split(",")[0] == "Zamazenta-Crowned":
                swapIndex = pokemon[i][0].index("Zamazenta")
            elif blocks[3].split(",")[0] == "Zacian-Crowned":
                swapIndex = pokemon[i][0].index("Zacian")
            elif blocks[3].split(",")[0] == "Urshifu-Rapid-Strike" \
                    or blocks[3].split(",")[0] == "Urshifu-Single-Strike":
                swapIndex = pokemon[i][0].index("Urshifu")
            elif blocks[3].split(",")[0] == "Mimikyu-Busted":
                swapIndex = pokemon[i][0].index("Mimikyu")
            elif blocks[3].split(",")[0] == "Ogerpon-Teal-Tera" or blocks[3].split(",")[0] == "Ogerpon-Wellspring-Tera":
                for j in range(6):
                    if pokemon[i][0][j].startswith("Ogerpon"):
                        swapIndex = j
            elif blocks[3].split(",")[0] == "Indeedee-F":
                swapIndex = pokemon[i][0].index("Indeedee")
            else:
                swapIndex = pokemon[i][0].index(blocks[3].split(",")[0])
            moves[i] = (hash_pkmn.loc[hash_pkmn['Name'] == pokemon[i][0][swapIndex]])['Number']
            add_action(actions, hash_pkmn, hash_moves, currPkmn, currBoosts, currWeather, currTerrain, currHazards,
                       moves, i)
            pokemon[i][0][0], pokemon[i][0][swapIndex] = pokemon[i][0][swapIndex], pokemon[i][0][0]
            pokemon[i][1][0], pokemon[i][1][swapIndex] = pokemon[i][1][swapIndex], pokemon[i][1][0]
            boosts[i] = boosts_zero
            pokemon[i][2][0], pokemon[i][2][swapIndex] = pokemon[i][2][swapIndex], pokemon[i][2][0]
            pokemon[i][3][0], pokemon[i][3][swapIndex] = pokemon[i][3][swapIndex], pokemon[i][3][0]
            pokemon[i][4][0], pokemon[i][4][swapIndex] = pokemon[i][4][swapIndex], pokemon[i][4][0]
        elif blocks[1] == 'drag':
            i = 0 if blocks[2].startswith('p1') else 1
            pokemon[i][0][0], pokemon[i][0][5] = pokemon[i][0][5], pokemon[i][0][0]
            pokemon[i][1][0], pokemon[i][1][5] = pokemon[i][1][5], pokemon[i][1][0]
            boosts[i] = boosts_zero
            pokemon[i][2][0], pokemon[i][2][5] = pokemon[i][2][5], pokemon[i][2][0]
            pokemon[i][3][0], pokemon[i][3][5] = pokemon[i][3][5], pokemon[i][3][0]
            pokemon[i][4][0], pokemon[i][4][5] = pokemon[i][4][5], pokemon[i][4][0]
        elif blocks[1] == 'move':
            i = 0 if blocks[2].startswith('p1') else 1
            moves[i] = blocks[3]
            add_action(actions, hash_pkmn, hash_moves, currPkmn, currBoosts, currWeather, currTerrain, currHazards,
                       moves, i)
        elif blocks[1] == '-damage' or blocks[1] == '-heal':
            i = 0 if blocks[2].startswith('p1') else 1
            pokemon[i][1][0] = int(blocks[3].split(" ")[0].split("/")[0])
        elif blocks[1] == '-boost' or blocks[1] == '-unboost':
            i = 0 if blocks[2].startswith('p1') else 1
            change = int(blocks[4]) * -1 if blocks[1].startswith('-un') else 1
            boosts[i][blocks[3]] += change
        elif blocks[1] == '-fieldstart':
            terr_temp = blocks[2].split(" ")[1]
            if terr_temp == 'Electric':
                terrain = 1
            elif terr_temp == 'Psychic':
                terrain = 2
            elif terr_temp == 'Misty':
                terrain = 3
            elif terr_temp == 'Grassy':
                terrain = 4
        elif blocks[1] == '-fieldend':
            terrain = 0
        elif blocks[1] == '-weather':
            weath_temp = blocks[2]
            if weath_temp == 'none':
                weather = 0
            elif weath_temp == 'SunnyDay':
                weather = 1
            elif weath_temp == 'Snow':
                weather = 2
            elif weath_temp == 'Rain':
                weather = 3
            elif weath_temp == 'Sandstorm':
                weather = 4
        elif blocks[1] == '-sidestart':
            i = 0 if blocks[2].startswith('p1') else 1
            if ':' in blocks[3]:
                hazards[i][blocks[3].split(': ')[1]] += 1
            else:
                hazards[i][blocks[3]] += 1
        elif blocks[1] == '-sideend':
            i = 0 if blocks[2].startswith('p1') else 1
            if ':' in blocks[3]:
                hazards[i][blocks[3].split(': ')[1]] = 0
            else:
                hazards[i][blocks[3]] = 0
        elif blocks[1] == '-swapsideconditions':
            hazards[0], hazards[1] = hazards[1], hazards[0]
        elif blocks[1] == 'turn' or blocks[1] == 'upkeep':
            currPkmn = pokemon
            currBoosts = boosts
            currWeather = weather
            currTerrain = terrain
            currHazards = hazards


def create_table(links_input, turnsTable):
    actions = []

    move_data = pd.ExcelFile('moves.xlsx')
    dfm = pd.read_excel(move_data, sheet_name=0)
    hash_moves = pd.Series(dfm['id'].values, index=dfm['name']).to_dict()
    hash_pkmn = pd.read_excel('better_pkmn_data.xlsx')

    with open(links_input, 'r') as f:
        links = f.read()
    i = 1
    for link in links.split("\n"):
        try:
            parse(link + ".log", actions, hash_pkmn, hash_moves, i)
        except Exception as e:
            print(e)
        i += 1

    df = pd.DataFrame(actions)
    df.to_csv(turnsTable, index=False)
