import pandas as pd
import database as db
import sqlalchemy
from schemas import pokemon_final
from databasesync import Typespk

def GetPokemonFinal(pokemon_id):

    with db.engine.begin() as conn:

        result = conn.execute(
            sqlalchemy
            .select(pokemon_final)
            .where(pokemon_final.c.pokedex_number == pokemon_id)
        )
    return result.first()

def GetPokemonFinalTypesIdsAndStats(pokemon_id):
    
        with db.engine.begin() as conn:
    
            result = conn.execute(
                sqlalchemy
                .select(pokemon_final.c.type1, pokemon_final.c.type2,
                        pokemon_final.c.HP, pokemon_final.c.Atk,
                        pokemon_final.c.Def, pokemon_final.c.SpA,
                        pokemon_final.c.SpD, pokemon_final.c.Spe)
                .where(pokemon_final.c.pokedex_number == pokemon_id)
            )
        return result.first()

def GetPokemonFinalTypeNamesAndStats(pokemon_id):
    
        with db.engine.begin() as conn:
    
            result = conn.execute(
                sqlalchemy
                .select(pokemon_final.c.type1, pokemon_final.c.type2,
                        pokemon_final.c.HP, pokemon_final.c.Atk,
                        pokemon_final.c.Def, pokemon_final.c.SpA,
                        pokemon_final.c.SpD, pokemon_final.c.Spe)
                .where(pokemon_final.c.pokedex_number == pokemon_id)
            )
        pokemon = result.first()
        return (Typespk[pokemon[0]], Typespk[pokemon[1]], pokemon[2], pokemon[3],
                pokemon[4], pokemon[5], pokemon[6], pokemon[7])

def ReOrderList(pokemonids, pokemonlist):
    pokemonlist = pd.DataFrame(pokemonlist, columns=["pokedex_number", "type1", "type2", "HP", "Atk", "Def", "SpA", "SpD", "Spe"])
    pokemonlist = pokemonlist.set_index("pokedex_number")
    pokemonlist = pokemonlist.reindex(pokemonids)
    pokemonlist = pokemonlist.reset_index()
    return pokemonlist.values.tolist()
    

def GetPokemonTypeAndStatsList(pokemon_ids, TypeIds = False):
        
        
        with db.engine.begin() as conn:
    
            result = conn.execute(
                sqlalchemy
                .select(pokemon_final.c.pokedex_number, pokemon_final.c.type1, pokemon_final.c.type2,
                        pokemon_final.c.HP, pokemon_final.c.Atk,
                        pokemon_final.c.Def, pokemon_final.c.SpA,
                        pokemon_final.c.SpD, pokemon_final.c.Spe)
                .where(pokemon_final.c.pokedex_number.in_(pokemon_ids))
            )

        pokemon = ReOrderList(pokemon_ids, result.fetchall())

        if TypeIds:
            return [(row[0], row[1], row[2], row[3], row[4],
                    row[5], row[6], row[7], row[8]) for row in pokemon]
        else:
            return [(row[0], Typespk[row[1]], Typespk[row[2]], row[3], row[4],
                row[5], row[6], row[7], row[8]) for row in pokemon]



def GetListPokemonFinal(pokemon_ids):

    with db.engine.begin() as conn:

        result = conn.execute(
            sqlalchemy
            .select(pokemon_final)
            .where(pokemon_final.c.pokedex_number.in_(pokemon_ids))
        )
    return result.fetchall()