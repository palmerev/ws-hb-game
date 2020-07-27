from typing import Optional, Dict, List, Any
import uuid

import attr
from fastapi import (
    Cookie,
    FastAPI,
    Response,
    status,
    WebSocket,
)
from starlette.websockets import WebSocketDisconnect
from fastapi.responses import HTMLResponse

from utils import gen_client_id, msg
from utils import HBPlayer, HBPlayerOut, GameOut, Game
from gameid import gen_game_id

MAX_GAMES = 20
MAX_PLAYERS_PER_GAME = 10
WS_KEY = 'sec-websocket-key'

# maps game id to Game object
GAMES = {}


class GameLockedException(Exception):
    pass


app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.websocket("/ws/hbgame/{game_id}")
async def ws_hbgame_handler(websocket: WebSocket, game_id: str, client_id: Optional[str] = Cookie(None)):
    try:
        await websocket.accept()
        print(websocket.__dict__)
        while True:
            data = await websocket.receive_json()
            print(f"GAME HANDLER: {data} {type(data)}")
    #         print(f"received message {data} from {id(websocket)}")
            if not client_id:
                await websocket.send_json({
                    "type": "error",
                    "msg": "missing client id"
                })
            else:
                print('client_id:', client_id)
            for game in GAMES.values():
                for player in game.players:
                    if (player.client_id == client_id
                        and player.websocket != websocket):
                        player.websocket = websocket
            if data['type'] == "ping":
                await websocket.send_json({"type": "pong"})
            elif data['type'] == "preJoin":
                # 'join' event adds player to game if possible
                # returns all players in that game (including added player) OR error
                print('got "preJoin" event', data)
                if game_id in GAMES:
                    game = GAMES[game_id]
#                     print(f'game: {GAMES[game_id].dict()}')
                    if not game.has_player(client_id):
                        game.add_player(HBPlayer(
                            nickname=f'Player {game.player_count + 1}',
                            client_id=client_id,
                            websocket=websocket,
                        ))
                    game_out = GameOut.parse_obj(GAMES[game_id].dict())
                    print(f'preJoin response: {game_out}')
                    game_sockets = game.sockets()
                    for ws in game_sockets:
                        await ws.send_json({"type": "preJoin", "game": game_out.dict()})
                else:
                    await websocket.close(code=1000)  # game id doesn't exist
            else:
                pass
    except WebSocketDisconnect as e:
        print("disconnected", client_id, e.code)
        game_ids_to_remove = set()
#        TOO AGGRESSIVE, NOT FAULT TOLERANT
#        for game in GAMES.values():
#             players = [p for p in game.players if p.websocket == websocket]
#             for p in players:
#                 game.remove_player(p.client_id)
#                 print(f'removed player {p.nickname} {p.client_id}')
#             if game.player_count == 0:
#                 games_to_remove.append(game.id)
#         for gid in game_ids_to_remove:
#             print(f'deleting game {gid}')
#             del GAMES[gid]


@app.get("/hb/join-game/{game_id}")
async def join_hb_game(game_id: str, response: Response, client_id: Optional[str] = Cookie(None)):
    if not client_id:
        response.set_cookie(key="client_id", value=gen_client_id(), max_age=60 * 60 * 25, samesite='strict')
    if game_id in GAMES and len(GAMES[game_id].players) < MAX_PLAYERS_PER_GAME:
        return {"gameId": game_id}
    elif game_id not in GAMES:
        return {"error": "Invalid game ID"}
    elif len(GAMES[game_id].players) >= MAX_PLAYERS_PER_GAME:
        return {"error": f"This game already has {MAX_PLAYERS_PER_GAME} players"}
    else:
        return {"error": "Couldn't join the game for some reason."}


@app.post("/hb/create-game", status_code=status.HTTP_201_CREATED)
async def create_hb_game(data: Dict, response: Response):
    print(f"request to create game: {data}")
    # TODO: limit number of games one client can start (based on cookie)
    if len(GAMES) >= MAX_GAMES:
        return {"error": "too many games in progress"}
    game_id = gen_game_id()
    while game_id in GAMES:
        game_id = gen_game_id()
    game = Game(id=game_id)
    client_id: str = gen_client_id()
    player = HBPlayer(
        nickname=data.get('nickname', f'Player {game.player_count + 1}'),
        client_id=client_id,
    )
    game.add_player(player)
    GAMES[game.id] = game
    response.set_cookie(key="client_id", value=client_id, max_age=60 * 60 * 25, samesite='strict')
    return {"gameId": game.id}