import database as db
import sqlalchemy

from schemas import types, move_categories, players

#------------------------------------------------------------#
# Accessible variables
pkTypes = None
Typespk = None
pkMoveCategories = None
pkPlayers = None
#------------------------------------------------------------#

def SyncTypes():

    # Create a dictionary to store the primary keys with each type
    pkTypes = {}

    with db.engine.begin() as conn:

        result = conn.execute(
            sqlalchemy
            .select(types.c.id, types.c.type)
        )

        pkTypes = {row[1]: row[0] for row in result}
        Typespk = dict((v,k) for k,v in pkTypes.items())

    pkTypes[""] = 20
    Typespk[20] = None



    return (pkTypes, Typespk)

def SyncMoveCategories():

    # Create a dictionary to store the primary keys with each type
    pkMoveCategories = {}

    with db.engine.begin() as conn:

        result = conn.execute(
            sqlalchemy
            .select(move_categories.c.id, move_categories.c.category)
        )

        pkMoveCategories = {row[1]: row[0] for row in result}
        pkMoveCategories[""] = 4

    return pkMoveCategories

def SyncPlayers():

    # Create a dictionary to store the primary keys with each type
    pkPlayers = {}

    with db.engine.begin() as conn:

        result = conn.execute(
            sqlalchemy
            .select(players.c.id, players.c.username)
        )

        pkPlayers = {row[1].lower(): row[0] for row in result}

    return pkPlayers



(pkTypes, Typespk) = SyncTypes()
pkMoveCategories = SyncMoveCategories()
pkPlayers = SyncPlayers()
