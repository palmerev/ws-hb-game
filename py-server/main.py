from collections import OrderedDict

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

# CLIENTS = set() # top-level set of clients better for performance?

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

    def remove_player(self, player_id):
        self.players.pop(player_id)
        self.player_count = self.player_count

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
    emit('connectResponse', {'data': 'Server connected'})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


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
    if len(GAMES) >= MAX_GAMES:
        print('Error: can\'t create game. Too many games already in progress')
        emit('createGameResponse',
            {'error': "Error: Can\'t create game. Too many games already in progress"}
        )
    else:
        print('creating game')
        # prevent a client from joining more than one game at a time,
        # not including the first auto-generated room id (hence < 2)
        games = [g for g in GAMES.values() if data['username'] in g.players]
        if len() < 2:
            game_id = gen_game_id()
            join_room(game_id)
            if game_id not in GAMES:
                GAMES[game_id] = Game(game_id)
            emit('createGameResponse', {'gameId': game_id})
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
            emit('joinGameResponse', dict(data), room=data['gameId'])
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
