#!/usr/bin/env python3
import io
from os import system
from flask import app
from flask.helpers import send_file
import MySQLdb
import base64
import orjson as json
from PIL import Image
import yaml
import cloudscraper

from flask import Flask
app = Flask(__name__)

with open('config.yml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    conn = MySQLdb.connect(
    host=config['host'],
    port=int(config['port']),
    user=config['user'],
    passwd=config['password'],
    db=config['database'], 
    charset="utf8"
    )
conn.autocommit(True)

def get_cooking(image_url, image_size):
    scraper = cloudscraper.create_scraper()
    scraper_out = scraper.get(image_url, stream=True)
    print(image_url, scraper_out.status_code)
    if scraper_out.status_code == 404 or scraper_out.status_code == 403:
        return
    with Image.open(scraper_out.raw) as im:
        background = im.crop((8, 8, 16, 16)).convert("RGBA")
        foreground = im.crop((40, 8, 48, 16)).convert("RGBA")
        head = Image.alpha_composite(background, foreground)
        result = head.resize((image_size, image_size), resample=0)
        result_byte = io.BytesIO()
        result.save(result_byte, format='PNG')
        result_byte.seek(0)
        return send_file(result_byte, mimetype='image/png')


class GetUrl:
    def __init__(self, nick):
        self.nick = nick

    def mysql_query(self, sql):
        cursor = conn.cursor()
        q = "%s%%" % self.nick
        cursor.execute(sql, [q, ])
        row = cursor.fetchall()
        for myresult in row:
            return myresult

    def mysql_json(self, sql):
        cursor = conn.cursor()
        q = "%s%%" % self.nick
        cursor.execute(sql, [q, ])
        row = cursor.fetchall()
        for myresult in row:
            json_data = base64.urlsafe_b64decode(myresult[0])
            json_object = json.loads(json_data)
            return json_object


    def db_head(self):
        sql = "\
            SELECT Skins.Value \
            FROM Players \
            RIGHT JOIN Skins ON Players.Skin = Skins.Nick \
            WHERE Players.nick LIKE %s \
        "
        if self.mysql_json(sql) is None:
            return 
        else:
            return self.mysql_json(sql)['textures']['SKIN']['url']

    def premium_uuid(self):
        sql = "\
            SELECT premium.UUID \
            FROM premium \
            WHERE premium.Name LIKE %s \
        "
        if self.mysql_query(sql) is None:
            return
        else:
            return self.mysql_query(sql)[0]

    def mojang_head(self):
        scraper = cloudscraper.create_scraper()
        uuid_get = scraper.get(
            f'https://api.mojang.com/users/profiles/minecraft/{self.nick}', stream=True)
        if uuid_get.status_code == 404 or uuid_get.status_code == 204:
            print('can\'t find the skin, so we use steve\'s skin')
            return 'http://textures.minecraft.net/texture/1a4af718455d4aab528e7a61f86fa25e6a369d1768dcb13f7df319a713eb810b'
        uuid = uuid_get.json()['id']
        values = scraper.get(
            f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}', stream=True).json()['properties'][0]['value']
        json_data = base64.urlsafe_b64decode(values)
        json_object = json.loads(json_data)
        return json_object['textures']['SKIN']['url']

    def tl_head(self):
        url = "https://tlauncher.org/upload/all/nickname/tlauncher_{0}.png".format(self.nick)
        return url

def get_avatar(insert_nickname, avatar_size):
    nickname = GetUrl(insert_nickname)  # Name Input
    is_premium =  True if nickname.premium_uuid() is not None else False

    if nickname.db_head() is None:
        print(nickname.db_head())
        print(f'{insert_nickname} didn\'t have custom skin')
        if is_premium is True:
            print(f'{insert_nickname} is premium user')
            return get_cooking(nickname.mojang_head(), avatar_size)
        else:
            print(f'{insert_nickname} is not premium user')
            if get_cooking(nickname.tl_head(), avatar_size) is None:
                print(
                    f'can\'t find {insert_nickname} in TL so now we use Mojang')
                return get_cooking(nickname.mojang_head(), avatar_size)
            else:
                print(f'found {insert_nickname} in TL')
                return get_cooking(nickname.tl_head(), avatar_size)
    else:
        print(f'{insert_nickname} has custom skin')
        return get_cooking(nickname.db_head(), avatar_size)


@app.route('/<int:size>/<nickname>.png')
def serve_img(nickname, size):
    if size >= 512:
        size = 512
    nick_clean = str(nickname).lstrip(r"""!"#$%&'()*+,./:;<=>?@[\]^`{|}~""")
    img = get_avatar(nick_clean, size)
    return img

# if __name__ == "__main__":
#     try:
#         app.run(host='0.0.0.0', port=81, debug=True)
#     except KeyboardInterrupt:
#         system.exit(0)
