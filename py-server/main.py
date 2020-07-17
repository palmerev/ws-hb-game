from collections import OrderedDict, defaultdict
from typing import Optional

import attr
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from utils import gen_game_id, gen_client_id

MAX_GAMES = 5
MAX_PLAYERS = 10

# maps game id to Game object
GAMES = {}


@attr.s
class Game(object):
    game_id = attr.ib(type=str)
    players = attr.ib(factory=OrderedDict)

    def add_player(self, player):
        self.players[player.client_id] = player
        if self.player_count == 1:
            self.players[player.client_id].active = True

    def remove_player(self, client_id):
        return self.players.pop(client_id)

    def get_player(self, client_id):
        return self.players.get(client_id, None)

    def get_active_player(self):
        active_players = [p for p in self.players if p.active]
        if len(active_players) == 1:
            return active_players[0]
        else:
            raise Exception('Error: expected one active player, found', len(active_players))

    def has_player(self, client_id):
        return client_id in self.players

    @property
    def player_count(self):
        return len(self.players)

    def next_turn(self):
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
                next_idx = idx + 1 if idx + 1 < self.player_count else 0
                self.players[next_idx].active = True


@attr.s
class HBPlayer(object):
    sid = attr.ib(type=str)
    username = attr.ib(type=str)
    client_id = attr.ib(type=str, default='')
    tokens = attr.ib(type=int, default=3)
    word = attr.ib(type=str, default='')
    active = attr.ib(default=False)

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/test-ws")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(f"Received: {data} from {websocket.headers}")
        await websocket.send_text(f"Message text was: {data}")

