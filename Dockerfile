FROM python:2.7

RUN apt-get update && apt-get install -y \
    software-properties-common\
    apt-transport-https
RUN apt-key adv --fetch-keys --keyserver https://deb.nodesource.com/gpgkey/nodesource.gpg.key
RUN add-apt-repository -y -r ppa:chris-lea/node.js
RUN echo "deb https://deb.nodesource.com/node_5.x $(lsb_release -sc) main" > /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install -y --force-yes\
     nodejs
RUN npm install stylus -g
RUN mkdir /opt/src
ADD . /opt/src
WORKDIR /opt/src

RUN pip install -r requirements.txt
RUN pip install -e .
