import logging, os
from flask import app
from connection import redis_cache 
from player_data import GetUrl, IsIn
from style import style
from walrus import *
from dotenv import load_dotenv

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

CACHE_PLAYER_STATUS = int(os.getenv('CACHE_PLAYER_STATUS', 300))
CACHE_PLAYER_URL_TIME = int(os.getenv('CACHE_PLAYER_URL_TIME', 300))

db = redis_cache()

from flask import Flask
app = Flask(__name__)


def player_status_cache(nickname, method, name):
    if db.get(f'{nickname}_{name}') is None:
        if method is False:
            db.delete(f'{nickname}_{name}')
            db.set(f'{nickname}_{name}', 'False', CACHE_PLAYER_STATUS)
        else:
            db.delete(f'{nickname}_{name}')
            db.set(f'{nickname}_{name}', 'True', CACHE_PLAYER_STATUS)

def player_url_cache(nickname, the_url):
    if db.get(f'{nickname}_url') is None:
        db.delete(f'{nickname}_url')
        db.set(f'{nickname}_url', the_url, CACHE_PLAYER_URL_TIME)
        logging.info('%s\'s url is cached', str(nickname))
        return the_url
    else:
        logging.info('%s\'s url is in cache', str(nickname))
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
    
    logging.info('%s db: %s mjg: %s tl: %s', str(nickname), str(is_in_db), str(is_in_mojang), str(is_in_tl))


    if is_in_db == 'False':
        logging.info('%s didn\'t have custom skin', str(nickname))

        if is_in_mojang == 'True':
            logging.info('%s is premium user', str(nickname))
            head_url = player_url_cache(nickname, nickname_url.mojang_head())
            return style(head_url, avatar_size)

        else:
            logging.info('%s is not premium user', str(nickname))

            if is_in_tl == 'False':
                logging.info(
                    'can\'t find %s in TL so now we use Mojang insted', str(nickname))
                head_url = player_url_cache(
                    nickname, nickname_url.mojang_head())
                return style(head_url, avatar_size)

            else:
                logging.info('found %s in TL', str(nickname))
                head_url = player_url_cache(nickname, nickname_url.tl_head())
                return style(head_url, avatar_size)

    else:
        logging.info('%s has custom skin', str(nickname))
        head_url = player_url_cache(nickname, nickname_url.db_head())
        return style(head_url, avatar_size)


@app.route('/', strict_slashes=False)
@app.route('/<nickname>', strict_slashes=False)
@app.route('/<nickname>/<int:size>', strict_slashes=False)
@app.route('/<nickname>/<int:size>.png', strict_slashes=False)
@app.route('/<nickname>.png', strict_slashes=False)
@app.route('/<nickname>.png/<int:size>', strict_slashes=False)
@app.route('/<nickname>.png/<int:size>.png', strict_slashes=False)
@app.route('/<int:size>/<nickname>', strict_slashes=False)
@app.route('/<int:size>/<nickname>.png', strict_slashes=False)
def server_classic_png(nickname="null", size=230):
    if size >= 512:
        size = 512
    if size <= 8:
        size = 8
    nick_clean = str(nickname).lstrip(r"""!"#$%&'()*+,./:;<=>?@[\]^{|}~""")
    img = get_avatar(nick_clean, size)
    return img.classic_png()

@app.route('/<nickname>.jpg', strict_slashes=False)
@app.route('/<nickname>.jpg/<int:size>', strict_slashes=False)
@app.route('/<nickname>.jpg/<int:size>.jpg', strict_slashes=False)
@app.route('/<int:size>/<nickname>.jpg', strict_slashes=False)
def serve_classic_jpeg(nickname="null", size=230):
    if size >= 512:
        size = 512
    if size <= 8:
        size = 8
    nick_clean = str(nickname).lstrip(r"""!"#$%&'()*+,./:;<=>?@[\]^{|}~""")
    img = get_avatar(nick_clean, size)
    return img.classic_jpeg()
