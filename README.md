# SkinsRestorer-Avatar-API
simple python rest API that create Minecraft player avatar from local MySQL DB and TLauncher's website
# env file example
```bash
MYSQL_HOST="MariaDB" #no default value, non-optional, str
MYSQL_PORT=3306 #default value 3306, optional, int
MYSQL_USER="root" #no default value, non-optional, str
MYSQL_PASSWORD="password" #no default value, non-optional, str
MYSQL_DATABASE="db_name" #no default value, non-optional, str
REDIS_HOST="redis" #no default value, non-optional, str
REDIS_PORT=6379 #default value 6379, optional, int
REDIS_DATABASE=0 #default value 0, optional, int
CACHE_IMAGE_TIME=300 #default value 300, optional, int
JPEG_QUALITY=80 #default value 80, optional, int
CACHE_PLAYER_TIME=300 #default value 300, optional, int
CACHE_PLAYER_URL_TIME=300 #default value 300, optional, int
```
# how to run
```bash
# create env file and change it according to taste
$ touch .env

# activate the virtual env and install the dependency
$ ./env/bin/activate
$ pip3 install -r requirements.txt

# now you can run it using flask or gunicorn
$ flask run
$ gunicorn -w 4 -b 0.0.0.0:5000 app:app
```