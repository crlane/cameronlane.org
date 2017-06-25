ORG ?= crlane
BASE ?= blog-builder
TEST ?= ${BASE}-test
DEPLOY ?= ${BASE}-deploy

.PHONY: image deploy submodules test serve
.IGNORE: clean

all: image

submodules:
	@git submodules update --init --recursive

image:
	@docker build -t ${ORG}/${BASE} .

deploy:
	@docker run --rm ${ORG}/${BASE} sitebuilder deploy --delete

_test:
	@docker build -t ${ORG}/${TEST} . -f Dockerfile-test

test:  _test
	@docker run --rm ${ORG}/${TEST}

serve:
	@docker run --rm -it -v`pwd`/builder/pages:/opt/src/builder/pages -p8000:8000 ${ORG}/${BASE} sitebuilder serve --debug
