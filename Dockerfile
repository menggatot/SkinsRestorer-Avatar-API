FROM python:3.8-slim-buster

WORKDIR /app

RUN set -ex; \
    \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    git \
    default-libmysqlclient-dev \
    gcc;

RUN git clone https://github.com/mbahmodin/SkinsRestorer-Avatar-API.git /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]