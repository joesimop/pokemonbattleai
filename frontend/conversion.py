from dataclasses import dataclass

from .driver import PokemonInfo, MoveInfo, ModifierInfo, StartingPokemonInfo, BattlefieldInfo

@dataclass
class SerializedPokemonInfo:
    id: float
    type1: int
    type2: int
    hp: int
    atk: int
    def_: int
    spa: int
    spd: int
    spe: int


terrain_mappings = {
    'Electric': 1,
    'Psychic': 2,
    'Misty': 3,
    'Grassy': 4,
}

weather_mappings = {
    'Sun': 1,
    'Sandstorm': 2,
    'Snow': 3,
    'Rain': 4,
}

type_mappings = {
    '': 0,
    'Fire': 1,
    'Normal': 2,
    'Water': 3,
    'Grass': 4,
    'Electric': 5,
    'Ice': 6,
    'Fighting': 7,
    'Poison': 8,
    'Ground': 9,
    'Flying': 10,
    'Psychic': 11,
    'Bug': 12,
    'Rock': 13,
    'Ghost': 14,
    'Dragon': 15,
    'Dark': 16,
    'Steel': 17,
    'Fairy': 18,
}

def convert_terrain_from_name(terrain_name: str | None) -> int:
    return 0 if terrain_name is None else terrain_mappings[terrain_name]

def convert_weather_from_name(weather_name: str | None) -> int:
    return 0 if weather_name is None else weather_mappings[weather_name]

def load_pokemon_table(filename: str) -> dict[str, SerializedPokemonInfo]:
    pokemon_table: dict[str, SerializedPokemonInfo] = {}
    with open(filename, 'rt') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            id, name, _, type1, type2, hp, atk, def_, spa, spd, spe = line.split(',')
            if id == 'Number' or name in pokemon_table:
                continue
            pokemon_table[name] = SerializedPokemonInfo(
                float(id),
                type_mappings[type1],
                type_mappings[type2],
                int(hp),
                int(atk),
                int(def_),
                int(spa),
                int(spd),
                int(spe),
            )
    return pokemon_table

def serialize_data(
    pokemon_table: dict[str, SerializedPokemonInfo],
    player_pokemon: StartingPokemonInfo,
    player_bench: list[StartingPokemonInfo],
    player_status: ModifierInfo,
    enemy_pokemon: PokemonInfo,
    enemy_bench: list[PokemonInfo],
    enemy_status: ModifierInfo,
    battlefield: BattlefieldInfo,
) -> dict[str, int | float]:
    player_pokemon_conv = pokemon_table[player_pokemon.name]
    player_bench_conv = [pokemon_table[pokemon.name] for pokemon in player_bench]
    enemy_pokemon_conv = pokemon_table[enemy_pokemon.name]
    enemy_bench_conv = [pokemon_table[pokemon.name] for pokemon in enemy_bench]
    return {
        # player pokemon info
        'PlayerPkmnOnField': player_pokemon_conv.id,
        'PlayerPkmnHealth': player_pokemon.hp_percent,
        'PlayerBench1': player_bench_conv[0].id if len(player_bench_conv) > 0 else 0,
        'PlayerBenchOneHp': player_bench[0].hp_percent if len(player_bench) > 0 else 0,
        'PlayerBench2': player_bench_conv[1].id if len(player_bench_conv) > 1 else 0,
        'PlayerBenchTwoHp': player_bench[1].hp_percent if len(player_bench) > 1 else 0,
        'PlayerBench3': player_bench_conv[2].id if len(player_bench_conv) > 2 else 0,
        'PlayerBenchThreeHp': player_bench[2].hp_percent if len(player_bench) > 2 else 0,
        'PlayerBench4': player_bench_conv[3].id if len(player_bench_conv) > 3 else 0,
        'PlayerBenchFourHp': player_bench[3].hp_percent if len(player_bench) > 3 else 0,
        'PlayerBench5': player_bench_conv[4].id if len(player_bench_conv) > 4 else 0,
        'PlayerBenchFiveHp': player_bench[4].hp_percent if len(player_bench) > 4 else 0,
        'PlayerBoostAtk': player_status.atk,
        'PlayerBoostDef': player_status.def_,
        'PlayerBoostSpa': player_status.spa,
        'PlayerBoostSpd': player_status.spd,
        'PlayerBoostSpe': player_status.spe,
        'PlayerBoostEva': player_status.evasion,
        'PlayerBoostAcc': player_status.accuracy,

        # enemy pokemon info
        'EnemyPkmnOnField': enemy_pokemon_conv.id,
        'EnemyPkmnHealth': enemy_pokemon.hp_percent,
        'EnemyBench1': enemy_bench_conv[0].id if len(enemy_bench_conv) > 0 else 0,
        'EnemyBenchOneHp': enemy_bench[0].hp_percent if len(enemy_bench) > 0 else 0,
        'EnemyBench2': enemy_bench_conv[1].id if len(enemy_bench_conv) > 1 else 0,
        'EnemyBenchTwoHp': enemy_bench[1].hp_percent if len(enemy_bench) > 1 else 0,
        'EnemyBench3': enemy_bench_conv[2].id if len(enemy_bench_conv) > 2 else 0,
        'EnemyBenchThreeHp': enemy_bench[2].hp_percent if len(enemy_bench) > 2 else 0,
        'EnemyBench4': enemy_bench_conv[3].id if len(enemy_bench_conv) > 3 else 0,
        'EnemyBenchFourHp': enemy_bench[3].hp_percent if len(enemy_bench) > 3 else 0,
        'EnemyBench5': enemy_bench_conv[4].id if len(enemy_bench_conv) > 4 else 0,
        'EnemyBenchFiveHp': enemy_bench[4].hp_percent if len(enemy_bench) > 4 else 0,
        'EnemyBoostAtk': enemy_status.atk,
        'EnemyBoostDef': enemy_status.def_,
        'EnemyBoostSpa': enemy_status.spa,
        'EnemyBoostSpd': enemy_status.spd,
        'EnemyBoostSpe': enemy_status.spe,
        'EnemyBoostEva': enemy_status.evasion,
        'EnemyBoostAcc': enemy_status.accuracy,

        # battlefield status
        'Weather': convert_weather_from_name(battlefield.weather),
        'Terrain': convert_terrain_from_name(battlefield.terrain),
        'PlayerStealthRock': battlefield.my_hazards.count('Stealth Rock'),
        'PlayerSpikes': battlefield.my_hazards.count('Spikes'),
        'PlayerToxicSpikes': battlefield.my_hazards.count('Toxic Spikes'),
        'PlayerStickyWeb': battlefield.my_hazards.count('Sticky Web'),
        'PlayerReflect': battlefield.my_other.count('Reflect'),
        'PlayerLightScreen': battlefield.my_other.count('Light Screen'),
        'PlayerMist': battlefield.my_other.count('Mist'),
        'PlayerAuroraVeil': battlefield.my_other.count('Aurora Veil'),
        'PlayerSafeguard': battlefield.my_other.count('Safeguard'),
        'EnemyStealthRock': battlefield.enemy_hazards.count('Stealth Rock'),
        'EnemySpikes': battlefield.enemy_hazards.count('Spikes'),
        'EnemyToxicSpikes': battlefield.enemy_hazards.count('Toxic Spikes'),
        'EnemyStickyWeb': battlefield.enemy_hazards.count('Sticky Web'),
        'EnemyReflect': battlefield.enemy_other.count('Reflect'),
        'EnemyLightScreen': battlefield.enemy_other.count('Light Screen'),
        'EnemyMist': battlefield.enemy_other.count('Mist'),
        'EnemyAuroraVeil': battlefield.enemy_other.count('Aurora Veil'),
        'EnemySafeguard': battlefield.enemy_other.count('Safeguard'),

        # on-field information
        'PlayerPkmnOnField_Type 1': player_pokemon_conv.type1,
        'PlayerPkmnOnField_Type 2': player_pokemon_conv.type2,
        'PlayerPkmnOnField_HP': player_pokemon_conv.hp,
        'PlayerPkmnOnField_Atk': player_pokemon_conv.atk,
        'PlayerPkmnOnField_Def': player_pokemon_conv.def_,
        'PlayerPkmnOnField_SpA': player_pokemon_conv.spa,
        'PlayerPkmnOnField_SpD': player_pokemon_conv.spd,
        'PlayerPkmnOnField_Spe': player_pokemon_conv.spe,
        'EnemyPkmnOnField_Type 1': enemy_pokemon_conv.type1,
        'EnemyPkmnOnField_Type 2': enemy_pokemon_conv.type2,
        'EnemyPkmnOnField_HP': enemy_pokemon_conv.hp,
        'EnemyPkmnOnField_Atk': enemy_pokemon_conv.atk,
        'EnemyPkmnOnField_Def': enemy_pokemon_conv.def_,
        'EnemyPkmnOnField_SpA': enemy_pokemon_conv.spa,
        'EnemyPkmnOnField_SpD': enemy_pokemon_conv.spd,
        'EnemyPkmnOnField_Spe': enemy_pokemon_conv.spe,

        # player bench information
        'PlayerBench1_Type 1': player_bench_conv[0].type1 if len(player_bench_conv) > 0 else 0,
        'PlayerBench1_Type 2': player_bench_conv[0].type2 if len(player_bench_conv) > 0 else 0,
        'PlayerBench1_HP': player_bench_conv[0].hp if len(player_bench_conv) > 0 else 0,
        'PlayerBench1_Atk': player_bench_conv[0].atk if len(player_bench_conv) > 0 else 0,
        'PlayerBench1_Def': player_bench_conv[0].def_ if len(player_bench_conv) > 0 else 0,
        'PlayerBench1_SpA': player_bench_conv[0].spa if len(player_bench_conv) > 0 else 0,
        'PlayerBench1_SpD': player_bench_conv[0].spd if len(player_bench_conv) > 0 else 0,
        'PlayerBench1_Spe': player_bench_conv[0].spe if len(player_bench_conv) > 0 else 0,
        'PlayerBench2_Type 1': player_bench_conv[1].type1 if len(player_bench_conv) > 1 else 0,
        'PlayerBench2_Type 2': player_bench_conv[1].type2 if len(player_bench_conv) > 1 else 0,
        'PlayerBench2_HP': player_bench_conv[1].hp if len(player_bench_conv) > 1 else 0,
        'PlayerBench2_Atk': player_bench_conv[1].atk if len(player_bench_conv) > 1 else 0,
        'PlayerBench2_Def': player_bench_conv[1].def_ if len(player_bench_conv) > 1 else 0,
        'PlayerBench2_SpA': player_bench_conv[1].spa if len(player_bench_conv) > 1 else 0,
        'PlayerBench2_SpD': player_bench_conv[1].spd if len(player_bench_conv) > 1 else 0,
        'PlayerBench2_Spe': player_bench_conv[1].spe if len(player_bench_conv) > 1 else 0,
        'PlayerBench3_Type 1': player_bench_conv[2].type1 if len(player_bench_conv) > 2 else 0,
        'PlayerBench3_Type 2': player_bench_conv[2].type2 if len(player_bench_conv) > 2 else 0,
        'PlayerBench3_HP': player_bench_conv[2].hp if len(player_bench_conv) > 2 else 0,
        'PlayerBench3_Atk': player_bench_conv[2].atk if len(player_bench_conv) > 2 else 0,
        'PlayerBench3_Def': player_bench_conv[2].def_ if len(player_bench_conv) > 2 else 0,
        'PlayerBench3_SpA': player_bench_conv[2].spa if len(player_bench_conv) > 2 else 0,
        'PlayerBench3_SpD': player_bench_conv[2].spd if len(player_bench_conv) > 2 else 0,
        'PlayerBench3_Spe': player_bench_conv[2].spe if len(player_bench_conv) > 2 else 0,
        'PlayerBench4_Type 1': player_bench_conv[3].type1 if len(player_bench_conv) > 3 else 0,
        'PlayerBench4_Type 2': player_bench_conv[3].type2 if len(player_bench_conv) > 3 else 0,
        'PlayerBench4_HP': player_bench_conv[3].hp if len(player_bench_conv) > 3 else 0,
        'PlayerBench4_Atk': player_bench_conv[3].atk if len(player_bench_conv) > 3 else 0,
        'PlayerBench4_Def': player_bench_conv[3].def_ if len(player_bench_conv) > 3 else 0,
        'PlayerBench4_SpA': player_bench_conv[3].spa if len(player_bench_conv) > 3 else 0,
        'PlayerBench4_SpD': player_bench_conv[3].spd if len(player_bench_conv) > 3 else 0,
        'PlayerBench4_Spe': player_bench_conv[3].spe if len(player_bench_conv) > 3 else 0,
        'PlayerBench5_Type 1': player_bench_conv[4].type1 if len(player_bench_conv) > 4 else 0,
        'PlayerBench5_Type 2': player_bench_conv[4].type2 if len(player_bench_conv) > 4 else 0,
        'PlayerBench5_HP': player_bench_conv[4].hp if len(player_bench_conv) > 4 else 0,
        'PlayerBench5_Atk': player_bench_conv[4].atk if len(player_bench_conv) > 4 else 0,
        'PlayerBench5_Def': player_bench_conv[4].def_ if len(player_bench_conv) > 4 else 0,
        'PlayerBench5_SpA': player_bench_conv[4].spa if len(player_bench_conv) > 4 else 0,
        'PlayerBench5_SpD': player_bench_conv[4].spd if len(player_bench_conv) > 4 else 0,
        'PlayerBench5_Spe': player_bench_conv[4].spe if len(player_bench_conv) > 4 else 0,
        
        # enemy bench information
        'EnemyBench1_Type 1': enemy_bench_conv[0].type1 if len(enemy_bench_conv) > 0 else 0,
        'EnemyBench1_Type 2': enemy_bench_conv[0].type2 if len(enemy_bench_conv) > 0 else 0,
        'EnemyBench1_HP': enemy_bench_conv[0].hp if len(enemy_bench_conv) > 0 else 0,
        'EnemyBench1_Atk': enemy_bench_conv[0].atk if len(enemy_bench_conv) > 0 else 0,
        'EnemyBench1_Def': enemy_bench_conv[0].def_ if len(enemy_bench_conv) > 0 else 0,
        'EnemyBench1_SpA': enemy_bench_conv[0].spa if len(enemy_bench_conv) > 0 else 0,
        'EnemyBench1_SpD': enemy_bench_conv[0].spd if len(enemy_bench_conv) > 0 else 0,
        'EnemyBench1_Spe': enemy_bench_conv[0].spe if len(enemy_bench_conv) > 0 else 0,
        'EnemyBench2_Type 1': enemy_bench_conv[1].type1 if len(enemy_bench_conv) > 1 else 0,
        'EnemyBench2_Type 2': enemy_bench_conv[1].type2 if len(enemy_bench_conv) > 1 else 0,
        'EnemyBench2_HP': enemy_bench_conv[1].hp if len(enemy_bench_conv) > 1 else 0,
        'EnemyBench2_Atk': enemy_bench_conv[1].atk if len(enemy_bench_conv) > 1 else 0,
        'EnemyBench2_Def': enemy_bench_conv[1].def_ if len(enemy_bench_conv) > 1 else 0,
        'EnemyBench2_SpA': enemy_bench_conv[1].spa if len(enemy_bench_conv) > 1 else 0,
        'EnemyBench2_SpD': enemy_bench_conv[1].spd if len(enemy_bench_conv) > 1 else 0,
        'EnemyBench2_Spe': enemy_bench_conv[1].spe if len(enemy_bench_conv) > 1 else 0,
        'EnemyBench3_Type 1': enemy_bench_conv[2].type1 if len(enemy_bench_conv) > 2 else 0,
        'EnemyBench3_Type 2': enemy_bench_conv[2].type2 if len(enemy_bench_conv) > 2 else 0,
        'EnemyBench3_HP': enemy_bench_conv[2].hp if len(enemy_bench_conv) > 2 else 0,
        'EnemyBench3_Atk': enemy_bench_conv[2].atk if len(enemy_bench_conv) > 2 else 0,
        'EnemyBench3_Def': enemy_bench_conv[2].def_ if len(enemy_bench_conv) > 2 else 0,
        'EnemyBench3_SpA': enemy_bench_conv[2].spa if len(enemy_bench_conv) > 2 else 0,
        'EnemyBench3_SpD': enemy_bench_conv[2].spd if len(enemy_bench_conv) > 2 else 0,
        'EnemyBench3_Spe': enemy_bench_conv[2].spe if len(enemy_bench_conv) > 2 else 0,
        'EnemyBench4_Type 1': enemy_bench_conv[3].type1 if len(enemy_bench_conv) > 3 else 0,
        'EnemyBench4_Type 2': enemy_bench_conv[3].type2 if len(enemy_bench_conv) > 3 else 0,
        'EnemyBench4_HP': enemy_bench_conv[3].hp if len(enemy_bench_conv) > 3 else 0,
        'EnemyBench4_Atk': enemy_bench_conv[3].atk if len(enemy_bench_conv) > 3 else 0,
        'EnemyBench4_Def': enemy_bench_conv[3].def_ if len(enemy_bench_conv) > 3 else 0,
        'EnemyBench4_SpA': enemy_bench_conv[3].spa if len(enemy_bench_conv) > 3 else 0,
        'EnemyBench4_SpD': enemy_bench_conv[3].spd if len(enemy_bench_conv) > 3 else 0,
        'EnemyBench4_Spe': enemy_bench_conv[3].spe if len(enemy_bench_conv) > 3 else 0,
        'EnemyBench5_Type 1': enemy_bench_conv[4].type1 if len(enemy_bench_conv) > 4 else 0,
        'EnemyBench5_Type 2': enemy_bench_conv[4].type2 if len(enemy_bench_conv) > 4 else 0,
        'EnemyBench5_HP': enemy_bench_conv[4].hp if len(enemy_bench_conv) > 4 else 0,
        'EnemyBench5_Atk': enemy_bench_conv[4].atk if len(enemy_bench_conv) > 4 else 0,
        'EnemyBench5_Def': enemy_bench_conv[4].def_ if len(enemy_bench_conv) > 4 else 0,
        'EnemyBench5_SpA': enemy_bench_conv[4].spa if len(enemy_bench_conv) > 4 else 0,
        'EnemyBench5_SpD': enemy_bench_conv[4].spd if len(enemy_bench_conv) > 4 else 0,
        'EnemyBench5_Spe': enemy_bench_conv[4].spe if len(enemy_bench_conv) > 4 else 0,
    }
