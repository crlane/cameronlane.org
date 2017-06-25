FROM python:3.6.1-alpine3.6
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add nodejs yarn

RUN mkdir -p /opt/src
ADD . /opt/src
WORKDIR /opt/src
RUN yarn install
RUN yarn run build:prod

RUN python setup.py bdist_wheel
RUN pip install ./dist/*.whl
