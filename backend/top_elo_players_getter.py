import requests
from bs4 import BeautifulSoup
from sys import maxsize as MAX_INT
import json

from enum import Enum
from replay_utils import *


import database as db
import sqlalchemy
from schemas import players, elo_rankings
from databasesync import pkTypes, pkMoveCategories

#Returns the top 50 users in a given group
def GetTopEloUsersInGroup(gen, tier):

    tier = GetGenerationTierCombo(gen, tier)
    url = ladderUrl + tier + ".json"

    response = requests.get(url)

    if response.status_code == 200:
        jsonBody = json.loads(response._content)
        return jsonBody["toplist"][:50]                 #Only return the top 50 players

    else:
        print("Error: " + str(response.status_code))


def PutTopPlayersIntoDatabase(gen, tier):

    data = GetTopEloUsersInGroup(gen, tier)

    #Build database entries
    playerEntries = []
    eloEntries = []

    for entry in data:

        playerEntries.append(
            {
                "username": entry["username"],
                "userid": entry["userid"]
            }
        )

        eloEntries.append(
            {
                "userid": entry["userid"],      #This is only used for matching elo to playerids
                "elo": entry["elo"],
                "gen": Generation(gen).value,
                "tier": Tier(tier).ToString(),
            }
        )

    # Insert players and associated elo into database.
    # Not the most effecient, but sql alchemy was bugging out when I tried to do this in two queries
    with db.engine.begin() as conn:

        for entry in data:

            # Must use sql alchemy.text to use ON CONFLICT
            insertedPlayerId = conn.execute(
                sqlalchemy.text(
                    '''
                    INSERT INTO players (username, userid)
                    VALUES (:username, :userid)
                    ON CONFLICT ( userid ) DO NOTHING
                    RETURNING id
                    '''
                ),
                {
                    "username": entry["username"],
                    "userid": entry["userid"]
                }
            ).all()

            # If player already exists, get their id 
            if insertedPlayerId == []:  

                insertedPlayerId = conn.execute(
                    sqlalchemy
                    .select(players.c.id)
                    .where(players.c.userid == entry["userid"])   
                ).all()[0][0]

            else:
                insertedPlayerId = insertedPlayerId[0][0]


            # Insert elo into database
            conn.execute(
                sqlalchemy
                .insert(elo_rankings)
                .values(
                    player = insertedPlayerId,
                    elo = entry["elo"],
                    generation = Generation(gen).value,
                    tier = Tier(tier).ToString(),
                )
            )

            print("Inserted player: " + entry["username"] + " with elo: " + str(entry["elo"]))

  
PutTopPlayersIntoDatabase(Generation.VIII, Tier.OneVOne)