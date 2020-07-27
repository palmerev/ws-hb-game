import uuid
from typing import Any, List
from pydantic import BaseModel

def gen_client_id():
    return uuid.uuid4().hex


def msg(type: str, body: Any):
    if not type:
        raise TypeError('invalid message type')
    m = { "type": type }
    if body:
        m["body"] = body
    return m


class HBPlayerBase(BaseModel):
    nickname: str
    client_id: str = ''
    tokens: int = 3
    word: str = ''
    active: bool = False


class HBPlayerOut(HBPlayerBase):
    pass


class HBPlayer(HBPlayerBase):
    websocket: Any


class GameBase(BaseModel):
    id: str
    players: List[HBPlayerOut] = []
    is_started: bool = False


class GameOut(GameBase):
    pass


class Game(GameBase):
    is_locked: bool = False

    def add_player(self, player):
        if self.is_locked:
            raise GameLockedException('This game is locked, new players cannot join.')
        self.players.append(player)

    def remove_player(self, client_id):
        client_player = [p for p in self.players if p.client_id == client_id]
        if len(client_player) == 1:
            self.players = [x for x in filter(lambda p: p.client_id != client_player[0].client_id, self.players)]
            return client_player[0]

    def get_player(self, client_id):
        return [p for p in self.players if p.client_id == client_id][0]

    def get_active_player(self):
        active_players = [p for p in self.players if p.active]
        if not self.is_started:
            return None
        elif len(active_players) == 1:
            return active_players[0]
        else:
            raise Exception('Error: expected one active player, found', len(active_players))

    def has_player(self, client_id):
        return len([p for p in self.players if p.client_id == client_id]) > 0

    def sockets(self):
        return [p.websocket for p in self.players]

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

