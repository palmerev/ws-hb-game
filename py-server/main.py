from typing import Optional, Dict, List
import uuid

import attr
from fastapi import FastAPI, WebSocket, Response, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from utils import gen_client_id
from gameid import gen_game_id

MAX_GAMES = 20
MAX_PLAYERS_PER_GAME = 10

# maps game id to Game object
GAMES = {}


class GameLockedException(Exception):
    pass


@attr.s
class Game(object):
    id = attr.ib(type=str)  # slug, essentially
    players = attr.ib(factory=list)
    is_started = attr.ib(default=False)
    is_locked = attr.ib(default=False)

    def add_player(self, player):
        if self.is_locked:
            raise GameLockedException('This game is locked, new players cannot join.')
        self.players.append(player)

    def remove_player(self, client_id):
        return self.players.pop(client_id) if self.player_count > 0 else None

    def get_player(self, client_id):
        return self.players.get(client_id, None)

    def get_active_player(self):
        active_players = [p for p in self.players if p.active]
        if not self.is_started:
            return None
        elif len(active_players) == 1:
            return active_players[0]
        else:
            raise Exception('Error: expected one active player, found', len(active_players))

    def has_player(self, client_id):
        return client_id in self.players

    @property
    def player_count(self):
        return len(self.players)

    def start_next_turn(self):
        # find the index of the active player and set active = False
        # use index+1 to set the next active player (0 if index +1 == self.player_count()
        if self.player_count == 1:
            pass
        else:
            idx = None
            for i, player in self.players.items():
                if player.active:
                    idx = i
            if idx is None:
                print('Error: setting active player to 0')
                idx = 0
            else:
                self.players[idx].active = False
                next_idx = idx + 1 if idx + 1 < len(self.players) else 0
                self.players[next_idx].active = True


@attr.s
class HBPlayer(object):
    nickname = attr.ib(type=str)
    client_id = attr.ib(type=str, default='')
    tokens = attr.ib(type=int, default=3)
    word = attr.ib(type=str, default='')
    active = attr.ib(default=False)


class PlayerModel(BaseModel):
    nickname: str
    client_id: str
    tokens: int
    word: str
    active: bool


class GameModel(BaseModel):
    id: str
    players: List[PlayerModel] = []
    is_started: bool



app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.websocket("/ws/ping")
async def pong():
    return {"pong": True}



@app.post("/hb/create-game", status_code=status.HTTP_201_CREATED)
async def create_hb_game(data: Dict, response: Response):
    print(f"/hb received request to create game: {data}")
    # TODO: limit number of games one client can start (based on cookie)
    game_id = gen_game_id()
    while game_id in GAMES:
        game_id = gen_game_id()
    game = Game(game_id)
    player = HBPlayer(
        data.get('nickname', 'Player{}'.format(game.player_count + 1)),
        uuid.uuid4()
    )
    game.add_player(player)
    GAMES[game.id] = game
    response.set_cookie(key="flatcowhbclient", value="test-flatcowhblclient")
    return {
        "gameId": game.id,
        "nickname": data.get('nickname'),
        }

# html = """
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>Chat</title>
#     </head>
#     <body>
#         <h1>WebSocket Chat</h1>
#         <form action="" onsubmit="sendMessage(event)">
#             <input type="text" id="messageText" autocomplete="off"/>
#             <button>Send</button>
#         </form>
#         <ul id='messages'>
#         </ul>
#         <script>
#             var ws = new WebSocket("ws://localhost:8000/ws");
#             ws.onmessage = function(event) {
#                 var messages = document.getElementById('messages')
#                 var message = document.createElement('li')
#                 var content = document.createTextNode(event.data)
#                 message.appendChild(content)
#                 messages.appendChild(message)
#             };
#             function sendMessage(event) {
#                 var input = document.getElementById("messageText")
#                 ws.send(input.value)
#                 input.value = ''
#                 event.preventDefault()
#             }
#         </script>
#     </body>
# </html>
# """


# @app.get("/test-ws")
# async def get():
#     return HTMLResponse(html)


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket, response: Response):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         print(f"Received: {data}")
#         await websocket.send_text(f"Message text was: {data}")
