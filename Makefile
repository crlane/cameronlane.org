ORG ?= crlane
BASE ?= blog-builder
TEST ?= blog-builder-test
DEPLOY ?= blog-builder-deploy

.PHONY: image test-image deploy-image submodules test
.IGNORE: clean

all: image test-image

image:
	@docker build -t ${ORG}/${BASE} .

test-image:
	@docker build -t ${ORG}/${TEST} -f Dockerfile-test .

deploy-image:
	@docker build -t ${ORG}/${DEPLOY} -f Dockerfile-build .

submodules:
	@git submodules update --init --recursive

test: 
	@docker run --rm -v`pwd`:/opt/src ${ORG}/${TEST}

serve:
	@docker run --rm -it -v`pwd`/builder/pages:/opt/src/builder/pages -p8000:8000 ${ORG}/${BASE} sitebuilder serve --debug

clean:
	@docker stop ${TEST}
	@docker rm ${TEST}
