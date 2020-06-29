from collections import OrderedDict, defaultdict

from flask import Flask, render_template, request
from flask_socketio import (
    SocketIO,
    emit,
    join_room,
    leave_room,
    close_room
)
import attr

from utils import gen_game_id, gen_client_id

app = Flask(__name__)
app.config['SECRET_KEY'] = '023w8ythg08haw0ag8ashet08ahw308sphlcfnvas'
socketio = SocketIO(app)

MAX_GAMES = 5
MAX_PLAYERS = 10

CLIENTS = defaultdict(list)

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


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    if request.sid not in CLIENTS:
        client_id = gen_client_id()
    else:
        client_id = CLIENTS[request.sid]
    emit('connectResponse', {'clientId': client_id})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    del CLIENTS[request.sid]


@socketio.on_error_default
def handle_error():
    print('There was an error: sid={}, message={}, args={}'.format(
        request.sid,
        request.event['message'],
        request.event['args']
    ))


@socketio.on('createGame')
def handle_create_game(data, methods=['GET']):
    print('data', data)
    if 'clientId' not in data:
        print('Error: no clientId provided')
        emit('createGameResponse',
            {'error': "Error: no clientId provided."}
        )
    if len(GAMES) >= MAX_GAMES:
        print('Error: can\'t create game. Too many games already in progress')
        emit('createGameResponse',
            {'error': "Error: Can\'t create game. Too many games already in progress"}
        )
    else:
        print('creating game')
        # prevent a client from joining more than one game at a time,
        # not including the first auto-generated room id (hence < 2)
        games = [g for g in GAMES.values() if g.has_player(data['clientId'])]
        if len(games) < 2:
            game_id = gen_game_id()
            while game_id in GAMES:
                game_id = gen_game_id()
            new_game = Game(game_id)
            GAMES[game_id] = new_game
            new_game.add_player(HBPlayer(request.sid, data['username'], data['clientId']))
            response = {'gameId': game_id, 'game': attr.asdict(new_game)}
            print('createGameResponse', response)
            emit('createGameResponse', response)
        else:
            in_progress = ', '.join(games[1:])
            print('this client is already in game(s):', in_progress)
            emit(
                'createGameResponse',
                {'error': 'Error: this client is already in {} game(s)'.format(len(games))}
            )


@socketio.on('joinGame')
def handle_join_game(data, methods=['POST']):
    print('joining game')
    if 'gameId' in data and data['gameId'] in GAMES:
        count = GAMES[data['gameId']]
        if count >= MAX_PLAYERS:
            print('Game is full')
            emit('joinGameResponse',
                {'error': 'Error: game {} is full'.format(data['gameId'])}
            )
        else:
            join_room(data['gameId'])
            # TODO: validate data before returning
            emit('joinGameResponse', data, room=data['gameId'])
    else:
        socketio.emit('joinGameResponse',
            {'error': 'Error: game {} is full'.format(data['gameId'])}
        )


@socketio.on('leaveGame')
def handle_leave_game(data, methods=['POST']):
    print('leaving game')
    leave_room(data['room'])
    if data['room'] in GAMES:
        count = GAMES[data['room']]
        GAMES[data['room']] = count - 1 if count > 0 else 0
    emit('leaveGameResponse', {'message': 'You left the game.'})


@socketio.on('endGame')
def handle_end_game(data, methods=['POST']):
    print('ending game')
    close_room(data['gameId'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
