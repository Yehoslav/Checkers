#!/usr/bin/env python

import json
import asyncio
import secrets

from checkers import checkers as C
from checkers import utils as U
import websockets

import logging

logging.basicConfig(format="%(message)s", level=logging.WARNING)

JOIN = {}
WATCH = {}


async def play(websocket, game, player, connected):
    async for message in websocket:
        # parse a play event from the UI.
        event = json.loads(message)
        print(event)
        assert event["type"] == "play"
        action = event["action"]
        position = event["position"]


        if action == "get_moves":
            move_chains = C.get_moves(
                game[0], C.get_checker(C.Position(*position), game[1]), game[1] | game[2]
            )
            av_moves = [move[-1] for move_chain in move_chains for move in move_chain]
            event = {
                "type": "play",
                "action": "get_moves",
                "av_moves": av_moves,
                "checkers": [C.to_dict(checker) for checker in  game[1] | game[2]],
            }
            await websocket.send(json.dumps(event))
        if action == "move":
            print(event)
            C.move_checker(game[0],
                           C.get_checker(C.Position(event["init"]["file"], event["init"]["rank"]),
                                       game[1]),
                           C.Position(*position), game[1]| game[2])
            event = {
                "type": "play",
                "action": "move",
                "checkers": [C.to_dict(checker) for checker in  game[1] | game[2]],
            }
            await websocket.send(json.dumps(event))


async def start(websocket):
    game = C.create_board()
    connected = {websocket}
    join_key = secrets.token_hex(12)
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
            "checkers": [C.to_dict(checker) for checker in  game[1] | game[2]],
        }
        await websocket.send(json.dumps(event))

        # Recieve and process moves from the first player
        await play(websocket, game, "white", connected)
    finally:
        del JOIN[join_key]
        del WATCH[watch_key]


async def handler(websocket):
    # Recieve and pars the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    # if "join" in event:
    #     # Second player joins the game
    #     await join(websocket, event["join"])
    # elif "watch" in event:
    #     # spectator watches an existing game
    #     await watch(websocket, event["watch"])
    # else:
    #     # first player started a new game.
    #     await start(websocket)
    await start(websocket)


async def main():
    async with websockets.serve(handler, "192.168.1.6", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
