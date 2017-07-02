ORG ?= crlane
BASE ?= blog-builder
TEST ?= ${BASE}-test

.PHONY: image deploy submodules test serve
.IGNORE: clean

all: image test serve

submodules:
	@git submodules update --init --recursive

image:
	@docker build -t ${ORG}/${BASE} .

deploy:
	@docker run --rm -e CLOUDFRONT_ID=${CLOUDFRONT_ID} -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} ${ORG}/${BASE} sitebuilder deploy --delete

_test:
	@docker build -t ${ORG}/${TEST} . -f Dockerfile-test

test:  _test
	@docker run --rm ${ORG}/${TEST}

serve:
	@docker run --rm -it -v`pwd`/server/builder/pages:/opt/src/builder/pages -p8000:8000 ${ORG}/${BASE} sitebuilder serve --debug
