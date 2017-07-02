FROM alpine:3.6 as asset_builder
RUN apk --no-cache add nodejs yarn
RUN mkdir /assets
WORKDIR /assets
ADD client /assets
RUN yarn install
RUN yarn run favicon
RUN yarn run build:prod

FROM python:3.6.1-alpine
ENV PYTHONUNBUFFERED=1
RUN mkdir -p /opt/src
WORKDIR /opt/src
ADD server/ /opt/src/
COPY --from=asset_builder /assets/css /opt/src/builder/static/css
COPY --from=asset_builder /assets/js /opt/src/builder/static/js
COPY --from=asset_builder /assets/favicon.ico  /opt/src/builder/static
RUN python setup.py bdist_wheel
RUN pip install ./dist/*.whl
RUN sitebuilder build
