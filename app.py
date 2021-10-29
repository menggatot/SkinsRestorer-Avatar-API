from flask import app
from geturl import GetUrl
from avatar_style.classic import classic

from flask import Flask
app = Flask(__name__)


def get_avatar(insert_nickname, avatar_size):
    nickname = GetUrl(insert_nickname)  # Name Input
    is_premium =  True if nickname.premium_uuid() is not None else False

    if nickname.db_head() is None:
        print(f'{insert_nickname} didn\'t have custom skin')
        if is_premium is True:
            print(f'{insert_nickname} is premium user')
            return classic(nickname.mojang_head(), avatar_size)
        else:
            print(f'{insert_nickname} is not premium user')
            if classic(nickname.tl_head(), avatar_size) is None:
                print(
                    f'can\'t find {insert_nickname} in TL so now we use Mojang')
                return classic(nickname.mojang_head(), avatar_size)
            else:
                print(f'found {insert_nickname} in TL')
                return classic(nickname.tl_head(), avatar_size)
    else:
        print(f'{insert_nickname} has custom skin')
        return classic(nickname.db_head(), avatar_size)


@app.route('/<int:size>/<nickname>.png')
def serve_img(nickname, size):
    if size >= 512:
        size = 512
    nick_clean = str(nickname).lstrip(r"""!"#$%&'()*+,./:;<=>?@[\]^{|}~""")
    img = get_avatar(nick_clean, size)
    return img
