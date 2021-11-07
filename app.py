from flask import app
from connection import redis_cache 
from player_data import GetUrl, IsIn
from style import style
from walrus import *

db = redis_cache()

from flask import Flask
app = Flask(__name__)


def player_status_cache(nickname, method, name):
    if db.get(f'{nickname}_{name}') is None:
        print(name, 'Is False' if method is False else 'Is True')

        if method is False:
            db.delete(f'{nickname}_{name}')
            db.set(f'{nickname}_{name}', 'False', 300)
        else:
            db.delete(f'{nickname}_{name}')
            db.set(f'{nickname}_{name}', 'True', 300)

def player_url_cache(nickname, the_url):
    if db.get(f'{nickname}_url') is None:
        db.delete(f'{nickname}_url')
        db.set(f'{nickname}_url', the_url, 300)
        print(f'{nickname}\'s url is cached')
        return the_url
    else:
        print(f'{nickname}\'s url is in cache')
        return db.get(f'{nickname}_url').decode("utf-8")

def get_avatar(nickname, avatar_size):
    nickname_status = IsIn(nickname) 
    nickname_url = GetUrl(nickname)

    player_status_cache(nickname, nickname_status.is_in_db(), 'is_in_db')
    player_status_cache(nickname, nickname_status.is_in_tl(), 'is_in_tl')
    player_status_cache(nickname, nickname_status.is_in_mojang(), 'is_in_mojang')

    is_in_db = db.get(f'{nickname}_is_in_db').decode("utf-8")
    is_in_mojang = db.get(f'{nickname}_is_in_mojang').decode("utf-8")
    is_in_tl = db.get(f'{nickname}_is_in_tl').decode("utf-8")
    print('db:', is_in_db, 'mjg:', is_in_mojang, 'tl:', is_in_tl)

    # return style(nickname_url.mojang_head(), avatar_size).classic()

    if is_in_db == 'False':
        print(f'{nickname} didn\'t have custom skin', is_in_db)

        if is_in_mojang == 'True':
            print(f'{nickname} is premium user', is_in_mojang)
            head_url = player_url_cache(nickname, nickname_url.mojang_head())
            return style(head_url, avatar_size).classic()

        else:
            print(f'{nickname} is not premium user', is_in_mojang)

            if is_in_tl == 'False':
                print(
                    f'can\'t find {nickname} in TL so now we use Mojang', is_in_tl)
                head_url = player_url_cache(
                    nickname, nickname_url.mojang_head())
                return style(head_url, avatar_size).classic()

            else:
                print(f'found {nickname} in TL', is_in_tl)
                head_url = player_url_cache(nickname, nickname_url.tl_head())
                return style(head_url, avatar_size).classic()

    else:
        print(f'{nickname} has custom skin', is_in_db)
        head_url = player_url_cache(nickname, nickname_url.db_head())
        return style(head_url, avatar_size).classic()



@app.route('/<int:size>/<nickname>.png')
def serve_img(nickname, size):
    if size >= 512:
        size = 512
    nick_clean = str(nickname).lstrip(r"""!"#$%&'()*+,./:;<=>?@[\]^{|}~""")
    img = get_avatar(nick_clean, size)
    return img
