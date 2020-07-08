ROOT_DIR	:= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
MAKE_DIR	:= $(ROOT_DIR)/.make
BUILD_DIR	:= $(ROOT_DIR)/build

export BUILD_DIR

.PHONY: build
build:
	@sudo python3 setup.py build

.PHONY: install
install: build
	@python3 setup.py install

.PHONY: clean
clean:
	@python3 setup.py clean --all