from flask import app
from connection import redis_cache 
from geturl import GetUrl, IsIn
from avatar_style.classic import classic
from walrus import *

db = redis_cache()

from flask import Flask
app = Flask(__name__)


def cache_it(insert_nickname, method, name):
    if db.get(f'{insert_nickname}_{name}') is None:
        if method is True:
            db.delete(f'{insert_nickname}_{name}')
            db.set(f'{insert_nickname}_{name}', 'True', 300)
        else:
            db.delete(f'{insert_nickname}_{name}')
            db.set(f'{insert_nickname}_{name}', 'False', 300)

def get_avatar(insert_nickname, avatar_size):
    nickname = IsIn(insert_nickname)  # Name Input
    nickname_url = GetUrl(insert_nickname)

    cache_it(insert_nickname, nickname.is_in_db, 'is_in_db')
    cache_it(insert_nickname, nickname.is_in_tl, 'is_in_tl')
    cache_it(insert_nickname, nickname.is_in_mojang, 'is_in_mojang')
    
    is_in_db = db.get(f'{insert_nickname}_is_in_db').decode("utf-8")
    is_in_mojang = db.get(f'{insert_nickname}_is_in_mojang').decode("utf-8")
    is_in_tl = db.get(f'{insert_nickname}_is_in_tl').decode("utf-8")

    if is_in_db == 'False':
        print(f'{insert_nickname} didn\'t have custom skin', is_in_db)

        if is_in_mojang == 'True':
            print(f'{insert_nickname} is premium user', is_in_mojang)
            return classic(nickname_url.mojang_head(), avatar_size)

        else:
            print(f'{insert_nickname} is not premium user', is_in_mojang)

            if is_in_tl == 'False':
                print(
                    f'can\'t find {insert_nickname} in TL so now we use Mojang', is_in_tl)
                return classic(nickname_url.mojang_head(), avatar_size)

            else:
                print(f'found {insert_nickname} in TL', is_in_tl)
                return classic(nickname_url.tl_head(), avatar_size)

    else:
        print(f'{insert_nickname} has custom skin',
              db.get(f'{insert_nickname}_is_in_db'))
        return classic(nickname_url.db_head(), avatar_size)

@app.route('/<int:size>/<nickname>.png')
def serve_img(nickname, size):
    if size >= 512:
        size = 512
    nick_clean = str(nickname).lstrip(r"""!"#$%&'()*+,./:;<=>?@[\]^{|}~""")
    img = get_avatar(nick_clean, size)
    return img
