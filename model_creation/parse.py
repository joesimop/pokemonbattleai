from typing import List, Union
import logging
import urllib.request
import pandas as pd


def add_action(actions, hash_pkmn, hash_moves, pokemon, boosts, moves, user):
    if user == 0:
        i, j = 0, 1
    else:
        i, j = 1, 0
    action_info = {
        'PlayerPkmnOnField': hash_pkmn[pokemon[i][0][0]],
        'PlayerPkmnHealth': pokemon[i][1][0],
        'PlayerBenchOne': hash_pkmn[pokemon[i][0][1]],
        'PlayerBenchOneHp': pokemon[i][1][1],
        'PlayerBenchTwo': hash_pkmn[pokemon[i][0][2]],
        'PlayerBenchTwoHp': pokemon[i][1][2],
        'PlayerBenchThree': hash_pkmn[pokemon[i][0][3]],
        'PlayerBenchThreeHp': pokemon[i][1][3],
        'PlayerBenchFour': hash_pkmn[pokemon[i][0][4]],
        'PlayerBenchFourHp': pokemon[i][1][4],
        'PlayerBenchFive': hash_pkmn[pokemon[i][0][5]],
        'PlayerBenchFiveHp': pokemon[i][1][5],
        'PlayerBoostAtk': boosts[i]["atk"],
        'PlayerBoostDef': boosts[i]["def"],
        'PlayerBoostSpa': boosts[i]["spa"],
        'PlayerBoostSpd': boosts[i]["spd"],
        'PlayerBoostSpe': boosts[i]["spe"],
        'PlayerBoostEva': boosts[i]["evasion"],
        'PlayerBoostAcc': boosts[i]["accuracy"],
        'EnemyPkmnOnField': hash_pkmn[pokemon[j][0][0]],
        'EnemyPkmnHealth': pokemon[j][1][0],
        'EnemyBenchOne': hash_pkmn[pokemon[j][0][1]],
        'EnemyBenchOneHp': pokemon[j][1][1],
        'EnemyBenchTwo': hash_pkmn[pokemon[j][0][2]],
        'EnemyBenchTwoHp': pokemon[j][1][2],
        'EnemyBenchThree': hash_pkmn[pokemon[j][0][3]],
        'EnemyBenchThreeHp': pokemon[j][1][3],
        'EnemyBenchFour': hash_pkmn[pokemon[j][0][4]],
        'EnemyBenchFourHp': pokemon[j][1][4],
        'EnemyBenchFive': hash_pkmn[pokemon[j][0][5]],
        'EnemyBenchFiveHp': pokemon[j][1][5],
        'EnemyBoostAtk': boosts[j]["atk"],
        'EnemyBoostDef': boosts[j]["def"],
        'EnemyBoostSpa': boosts[j]["spa"],
        'EnemyBoostSpd': boosts[j]["spd"],
        'EnemyBoostSpe': boosts[j]["spe"],
        'EnemyBoostEva': boosts[j]["evasion"],
        'EnemyBoostAcc': boosts[j]["accuracy"],
        'PlayerMove': None if moves[i] is None else hash_moves[moves[i]],
    }
    actions.append(action_info)


def parse(link, actions, hash_pkmn, hash_moves):
    pokemon: List[List[Union[List[str], List[int]]]] = [[[], [100] * 6], [[], [100] * 6]]
    boosts_zero = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0}
    boosts = [{"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0},
              {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0}]
    moves = [None, None]

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

    print(link)
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
            pokemon[i][0].append(blocks[3].split(',')[0].split('-*')[0])
        elif blocks[1] == 'switch':
            i = 0 if blocks[2].startswith('p1') else 1
            moves[i] = "switch"
            add_action(actions, hash_pkmn, hash_moves, pokemon, boosts, moves, i)
            if blocks[3].split(",")[0] == "Zamazenta-Crowned":
                swapIndex = pokemon[i][0].index("Zamazenta")
            elif blocks[3].split(",")[0] == "Zacian-Crowned":
                swapIndex = pokemon[i][0].index("Zacian")
            elif blocks[3].split(",")[0] == "Urshifu-Rapid-Strike" \
                    or blocks[3].split(",")[0] == "Urshifu-Single-Strike":
                swapIndex = pokemon[i][0].index("Urshifu")
            else:
                swapIndex = pokemon[i][0].index(blocks[3].split(",")[0])
            pokemon[i][0][0], pokemon[i][0][swapIndex] = pokemon[i][0][swapIndex], pokemon[i][0][0]
            pokemon[i][1][0], pokemon[i][1][swapIndex] = pokemon[i][1][swapIndex], pokemon[i][1][0]
            boosts[i] = boosts_zero
        elif blocks[1] == 'drag':
            i = 0 if blocks[2].startswith('p1') else 1
            pokemon[i][0][0], pokemon[i][0][5] = pokemon[i][0][5], pokemon[i][0][0]
            pokemon[i][1][0], pokemon[i][1][5] = pokemon[i][1][5], pokemon[i][1][0]
            boosts[i] = boosts_zero
        elif blocks[1] == 'move':
            i = 0 if blocks[2].startswith('p1') else 1
            moves[i] = blocks[3]
            add_action(actions, hash_pkmn, hash_moves, pokemon, boosts, moves, i)
        elif blocks[1] == '-damage' or blocks[1] == '-heal':
            i = 0 if blocks[2].startswith('p1') else 1
            pokemon[i][1][0] = int(blocks[3].split(" ")[0].split("/")[0])
        elif blocks[1] == '-boost' or blocks[1] == '-unboost':
            i = 0 if blocks[2].startswith('p1') else 1
            change = int(blocks[4]) * -1 if blocks[1].startswith('-un') else 1
            boosts[i][blocks[3]] += change


def create_table():
    actions = []

    move_data = pd.ExcelFile('moves.xlsx')
    dfm = pd.read_excel(move_data, sheet_name=0)
    hash_moves = pd.Series(dfm['id'].values, index=dfm['name']).to_dict()

    pkmn_data = pd.ExcelFile('pokemon_data.xlsx')
    dfp = pd.read_excel(pkmn_data, sheet_name=0)
    hash_pkmn = pd.Series(dfp.iloc[:, 0].values, index=dfp.iloc[:, 1]).to_dict()

    with open('links.txt', 'r') as f:
        links = f.read()
    for link in links.split("\n"):
        try:
            parse(link + ".log", actions, hash_pkmn, hash_moves)
        except Exception as e:
            print(e)

    df = pd.DataFrame(actions)
    df.to_csv('turns.csv', index=False)
