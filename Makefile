ORG ?= crlane
BASE ?= blog-builder
TEST ?= ${BASE}-test
DEPLOY ?= ${BASE}-deploy

.PHONY: image deploy submodules test serve
.IGNORE: clean

all: image test-image

image:
	@docker build -t ${ORG}/${BASE} .

_test:
	@docker build -t ${ORG}/${TEST} . -f Dockerfile-test

_install:
	@pip install .

deploy: _install
	@sitebuilder deploy

submodules:
	@git submodules update --init --recursive

test:  _test
	@docker run --rm ${ORG}/${TEST}

serve:
	@docker run --rm -it -v`pwd`/builder/pages:/opt/src/builder/pages -p8000:8000 ${ORG}/${BASE} sitebuilder serve --debug

clean:
	@docker stop ${TEST}
	@docker rm ${TEST}
