#
# IMPORTANT:
# All automatated tasks are run by invoke.
# This Makefile only ensures compatibility with our
# linting and testing docker image.
#

.PHONY: lint test

# Docker stuff
TAG?=dev  # You can inject it from the outside
LOCAL_IMAGE_NAME = 'images:local'
PUBLIC_IMAGE_NAME = None


lint:
	inv lint

test:
	inv test

docker-build:
	@docker build \
		-t $(LOCAL_IMAGE_NAME) \
		--build-arg VCS_REF=`git rev-parse --short HEAD` \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		.


compose:
	docker-compose up --build

clean-pyc:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	# find . -name '*~' -exec rm --force  {} +

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache

clean: clean-pyc clean-build
