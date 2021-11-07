# SkinsRestorer-Avatar-API
simple python rest API that create Minecraft player avatar from local MySQL DB and TLauncher's website
# env file example
```bash
MYSQL_HOST="MariaDB"
MYSQL_PORT="3306"
MYSQL_USER="root"
MYSQL_PASSWORD="password"
MYSQL_DATABASE="db_name"
REDIS_HOST="redis"
REDIS_PORT="6379"
REDIS_DATABASE="0"
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