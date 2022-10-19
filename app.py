#!/usr/bin/env python

import json
import asyncio
import secrets

from checkers import checkers as C
from checkers import utils as U
import websockets

from collections import namedtuple
import logging

logging.basicConfig(format="%(message)s", level=logging.WARNING)

JOIN = {}
WATCH = {}

Player = namedtuple("Player", "id skin")


async def play(websocket, game, connected):
    async for message in websocket:
        # parse a play event from the UI.
        event = json.loads(message)
        assert event["type"] == "play"
        action = event["action"]
        position = event["position"]
        player = [
            Player(val, key)
            for key, val in game[3].items()
            if val == event["player_id"]
        ]
        if len(player) != 1:
            raise ValueError("Too many, or no, players with the given id registered.")
        player = player[0]

        print(json.dumps(event, indent=2))
        print(player)

        if action == "get_moves":
            move_chains = C.get_moves(
                game[0],
                C.get_checker(
                    C.Position(*position),
                    game[1] if player.skin == "white" else game[2],
                ),
                game[1] | game[2],
            )
            av_moves = [move[-1] for move_chain in move_chains for move in move_chain]
            event = {
                "type": "play",
                "action": "get_moves",
                "av_moves": av_moves,
                "checkers": [C.to_dict(checker) for checker in game[1] | game[2]],
            }
            await websocket.send(json.dumps(event))
        if action == "move":
            C.move_checker(
                game[0],
                C.get_checker(
                    C.Position(event["init"]["file"], event["init"]["rank"]),
                    game[1] if player.skin == "white" else game[2],
                ),
                C.Position(*position),
                game[1] | game[2],
            )
            event = {
                "type": "play",
                "action": "move",
                "checkers": [C.to_dict(checker) for checker in game[1] | game[2]],
            }
            # await websocket.send(json.dumps(event))
            websockets.broadcast(connected, json.dumps(event), )


async def start(websocket, event):
    # TODO: Add a player ID associated with a checker color.
    connected = {websocket}
    join_key = secrets.token_hex(12)
    player_id = secrets.token_hex(10)
    game = *C.create_board(), {event["player_skin"]: player_id}
    JOIN[join_key] = game, connected

    watch_key = secrets.token_hex(12)
    WATCH[watch_key] = game, connected

    try:
        # Send the secret access token to the browser fo the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key,
            "watch_key": watch_key,
            "player_id": player_id,
            "checkers": [C.to_dict(checker) for checker in game[1] | game[2]],
        }
        await websocket.send(json.dumps(event))

        # Recieve and process moves from the first player
        await play(websocket, game, connected)
    finally:
        del JOIN[join_key]
        del WATCH[watch_key]


async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def join(websocket, join_key, event):
    # Find the Connect Four game.
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return
    else:
        player_id = secrets.token_hex(10)
        game[3][event["player_skin"]] = player_id
    # Register to receive moves from this game.
    connected.add(websocket)
    try:
        # Send the first move, in case the first player already played it.
        # await replay(websocket, game)
        # Temporary - for testing
        event = {
            "type": "join",
            "player_id": player_id,
            "checkers": [C.to_dict(checker) for checker in game[1] | game[2]],
        }

        await websocket.send(json.dumps(event))

        await play(websocket, game, connected)
    finally:
        connected.remove(websocket)

async def get_games(websocket):
    def is_two_players(game):
        return len(game[0][-1]) == 2

    games = [ {"join_key": game_id, "full": is_two_players(game)} 
             for game_id, game in JOIN.items()]
    event = {
        "type": "games",
        "games": games,
    }
    await websocket.send(json.dumps(event))

async def handler(websocket):
    # Recieve and pars the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # Second player joins the game
        await join(websocket, event["join"], event)
    # elif "watch" in event:
    #     # spectator watches an existing game
    #     await watch(websocket, event["watch"])
    elif "player_skin" in event:
        # first player started a new game.
        await start(websocket, event)
    else:
        await get_games(websocket)


async def main():
    async with websockets.serve(handler, "192.168.1.6", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
