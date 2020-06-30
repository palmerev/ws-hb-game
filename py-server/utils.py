import string
import random
import uuid


def gen_game_id(length=4):
    game_id = ''.join(random.choices(string.ascii_uppercase, k=length))
    print("generate_game_id:", game_id)
    return game_id


def gen_client_id():
    return uuid.uuid4().hex

if __name__ == '__main__':
    for x in range(0, 20):
        gen_game_id()
