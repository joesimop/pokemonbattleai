import requests
import json

from enum import Enum
from replay_utils import *


import database as db
import sqlalchemy
import datetime
import json
from schemas import replays, elo_rankings
from databasesync import pkPlayers


#Gets the top 50 replays for a user in a given group
def GetTopReplaysForUserInGroup(userid, gen, tier):

    group = GetGenerationTierCombo(gen, tier)

    url = replayBaseUrl + f"search.json?user={userid}&format={group}"
    response = requests.get(url)

    if response.status_code == 200:

        # To send to the database
        replaysForDatabase = []
        replays = json.loads(response._content)

        #If there are no replays, get outta here
        if replays == []:
            return

        for replay in replays:

            #Get the log of the replay
            log = GetReplayLog(replay["id"])

            #If we didn't get a log
            if log is None:
                 continue
            
            #Otherwise, add to replays
            else:
                #First we need to check if we have the other player in the database
                # If we dont, we will put them as unknown player
                # NOTE: we don't know whether the current userid will be p1 or p2, so do both
                player1 = pkPlayers.get(replay["p1"].lower(), None)
                player2 = pkPlayers.get(replay["p2"].lower(), None)

                # Convert to datetime object
                uploadTime = datetime.datetime.fromtimestamp(replay["uploadtime"])

                # Convert to database format
                replaysForDatabase.append( 
                    {
                        "replay_id": replay["id"].split("-")[-1],
                        "upload_time": uploadTime,
                        "player1": player1,
                        "player2": player2,
                        "tier": Tier(tier).ToString(),
                        "generation": Generation(gen).value,
                        "log": log
                    }
                )
    else:
        print("Error: " + str(response.status_code))

    with db.engine.begin() as conn:
        
        # Must use sql alchemy.text to use ON CONFLICT
        conn.execute(
            sqlalchemy.text(
                '''
                INSERT INTO replays (replay_id, upload_time, player1, player2, tier, generation, log)
                VALUES (:replay_id, :upload_time, :player1, :player2, :tier, :generation, :log)
                ON CONFLICT ( replay_id ) DO NOTHING
                '''
            ),
            replaysForDatabase
        )

    print(f"Added {len(replaysForDatabase)} replays for {userid} to database\n")

def GetReplayLog(id):
    
        url = replayBaseUrl + id + ".json?"
        response = requests.get(url)
    
        if response.status_code == 200:
            return json.loads(response._content)["log"]
    
        else:
            print("Error: " + str(response.status_code))
            return None
        

def GetReplaysForPlayersInDatabase():
         
    with db.engine.begin() as conn:

        unprocessedElos = conn.execute(
            sqlalchemy.text(

            '''
            SELECT players.userid, generation, tier
            FROM elo_rankings
            INNER JOIN players ON players.id = elo_rankings.player
            WHERE player IN (
                SELECT id
                FROM players
                EXCEPT
                SELECT DISTINCT COALESCE(player, 0) FROM 
                (
                    SELECT player1 AS player FROM replays
                    UNION SELECT player2 FROM replays
                ) foo
            )
            ORDER BY player
            '''
            )
        ).fetchall()

    for elo in unprocessedElos:
            print(f"Adding for {elo[0]}...")
            GetTopReplaysForUserInGroup(elo[0], Generation(elo[1]), Tier(elo[2]))

GetReplaysForPlayersInDatabase()