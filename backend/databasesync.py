import database as db
import sqlalchemy

from schemas import types, move_categories

#------------------------------------------------------------#
# Accessible variables
pkTypes = None
pkMoveCategories = None
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

    pkTypes[""] = 20

    return pkTypes

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



pkTypes = SyncTypes()
pkMoveCategories = SyncMoveCategories()
