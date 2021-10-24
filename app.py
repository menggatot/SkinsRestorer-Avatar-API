#!/usr/bin/env python3
import io
from os import system
from flask import app
from flask.helpers import send_file
import mysql.connector
import base64
import json
from PIL import Image
import yaml
import cloudscraper

from flask import Flask
app = Flask(__name__)

with open('config.yml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    mydb = mysql.connector.connect(
    host=config['host'],
    port=config['port'],
    user=config['user'],
    password=config['password'],
    database=config['database']
    )

def get_cooking(image_url, image_size):
    scraper = cloudscraper.create_scraper()
    scraper_out = scraper.get(image_url, stream=True)
    if scraper_out.status_code == 404:
        scraper_out = scraper.get("http://textures.minecraft.net/texture/b67168621fdb0cf3f7e57cb5166d48e9e9c87d677494339f3b8feec8c3a36b", stream=True)
    with Image.open(scraper_out.raw) as im:
        background = im.crop((8, 8, 16, 16)).convert("RGBA") 
        foreground = im.crop((40, 8, 48, 16)).convert("RGBA")
        head = Image.alpha_composite(background, foreground)
        result = head.resize((image_size, image_size), resample=0)
        result_byte = io.BytesIO()
        result.save(result_byte, format='PNG')
        result_byte.seek(0)
        return send_file(result_byte, mimetype='image/png')


class url:
    def __init__(self, nick):
        self.nick = nick

    def db_head(self):
        cursor = mydb.cursor()
        q = "%s%%" % self.nick
        # sql = "\
        #     SELECT Skins.Value \
        #     FROM Players \
        #     RIGHT JOIN Skins ON Players.Skin = Skins.Nick \
        #     WHERE Players.nick LIKE %s \
        # "
        sql = "\
            SELECT Skins.Value \
            FROM Skins \
            WHERE Skins.nick LIKE %s \
        "
        cursor.execute(sql, [q,])
        for myresult in cursor:
            json_data = base64.urlsafe_b64decode(myresult[0])
            json_object = json.loads(json_data)
            return json_object['textures']['SKIN']['url']

    def tl_head(self):
        url = "https://tlauncher.org/upload/all/nickname/tlauncher_{0}.png".format(self.nick)
        return url

def get_avatar(insert_nickname, avatar_size):
    nickname = url(insert_nickname)  # Name Input
    if nickname.db_head() is None:
        return get_cooking(nickname.tl_head(), avatar_size)
    else:
        return get_cooking(nickname.db_head(), avatar_size)

@app.route('/<int:size>/<nickname>.png')
def serve_img(nickname, size):
    img = get_avatar(nickname, size)
    return img

# if __name__ == "__main__":
#     try:
#         app.run(host='0.0.0.0', port=81, debug=True)
#     except KeyboardInterrupt:
#         system.exit(0)