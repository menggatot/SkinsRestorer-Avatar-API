import MySQLdb
import base64
import orjson as json
import os
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

def conn():
    conn = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DATABASE"),
        charset="utf8"
    )
    conn.autocommit(True)
    return conn


def mysql_query(sql, nick):
    cursor = conn().cursor()
    q = "%s%%" % nick
    cursor.execute(sql, [q, ])
    row = cursor.fetchall()
    for myresult in row:
        return myresult


def mysql_json(sql, nick):
    cursor = conn().cursor()
    q = "%s%%" % nick
    cursor.execute(sql, [q, ])
    row = cursor.fetchall()
    for myresult in row:
        json_data = base64.urlsafe_b64decode(myresult[0])
        json_object = json.loads(json_data)
        return json_object
