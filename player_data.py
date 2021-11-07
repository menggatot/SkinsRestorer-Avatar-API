from connection import mysql_json, mysql_query, redis_conn
import base64
import orjson as json
import cloudscraper
from walrus import *

db = redis_conn()

class GetUrl:
    def __init__(self, nick):
        self.nick = nick

    def db_head(self):
        sql = "\
            SELECT Skins.Value \
            FROM Players \
            RIGHT JOIN Skins ON Players.Skin = Skins.Nick \
            WHERE Players.nick LIKE %s \
        "
        if mysql_json(sql, self.nick) is None:
            return
        else:
            return mysql_json(sql, self.nick)['textures']['SKIN']['url']

    def premium_uuid(self):
        sql = "\
            SELECT premium.UUID \
            FROM premium \
            WHERE premium.Name LIKE %s \
        "
        if mysql_query(sql, self.nick) is None:
            return
        else:
            return mysql_query(sql, self.nick)[0]

    def mojang_head(self):
        scraper = cloudscraper.create_scraper()
        uuid_get = scraper.get(
            f'https://mc-heads.net/minecraft/profile/{self.nick}', stream=True)
        if uuid_get.status_code == 404 or uuid_get.status_code == 204:
            print('can\'t find the skin, so we use steve\'s skin')
            return 'https://mc-heads.net/avatar/c06f89064c8a49119c29ea1dbd1aab82'
        uuid = uuid_get.json()['id']
        values = scraper.get(
            f'https://mc-heads.net/minecraft/profile/{uuid}', stream=True).json()['properties'][0]['value']
        json_data = base64.urlsafe_b64decode(values)
        json_object = json.loads(json_data)
        return json_object['textures']['SKIN']['url']

    def tl_head(self):
        url = "https://tlauncher.org/upload/all/nickname/tlauncher_{0}.png".format(
            self.nick)
        return url

class IsIn:
    def __init__(self, nick):
        self.nick = nick

    def is_in_db(self):
        sql = "\
            SELECT Skins.Value \
            FROM Players \
            RIGHT JOIN Skins ON Players.Skin = Skins.Nick \
            WHERE Players.nick LIKE %s \
        "
        if mysql_query(sql, self.nick) is None:
            return False
        else:
            return True

    def is_in_mojang(self):
        scraper = cloudscraper.create_scraper()
        get_info = scraper.get(f'https://mc-heads.net/minecraft/profile/{self.nick}', stream=True)
        if get_info.status_code == 404 or get_info.status_code == 204:
            return False
        else:
            return True
    
    def is_in_tl(self):
        scraper = cloudscraper.create_scraper()
        get_info = scraper.get(f'https://tlauncher.org/upload/all/nickname/tlauncher_{self.nick}.png', stream=True)
        if get_info.status_code == 404 or get_info.status_code == 204:
            return False
        else:
            return True
