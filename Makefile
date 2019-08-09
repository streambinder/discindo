NAME := chopper
BIN := bin
BINARY_INSTALL_PATH := /usr/local/sbin
BINARY_INSTALL := $(BINARY_INSTALL_PATH)/$(NAME)
BINFILE := $(BIN)/$(NAME)
PYXFILE := $(BIN)/$(NAME).pyx
CFILE := $(BIN)/$(NAME).c
CFLAGS := -Os -I /usr/include/python3.6m -lpython3.6m -lpthread -lm -lutil -ldl

.PHONY: all
all: bin

.PHONY: bin
bin: c
	@ ( \
		gcc $(CFLAGS) -o $(BINFILE) $(CFILE); \
	);

.PHONY: c 	
c: prepare
	@ ( \
		cython -3 $(PYXFILE) -o $(CFILE) --embed; \
	);

.PHONY: prepare
prepare:
	@ ( \
		mkdir -p $(BIN); \
		find src/chopper -maxdepth 1 -type f -name \*.py -not -name __init__.py -exec cat {} > $(PYXFILE) \; ; \
		find src/chopper/providers -type f -name \*.py -not -name __init__.py -exec cat {} >> $(PYXFILE) \; ; \
		cat src/main.py >> $(PYXFILE); \
		sed -i '/^from\ \./d; /^from\ chopper/g' $(PYXFILE); \
	);

.PHONY: install
install: bin
	@ ( \
		(test -d $(BINARY_INSTALL_PATH) || install -D -d -m 00755 $(BINARY_INSTALL_PATH)) && \
		install -m 00755 $(BINFILE) $(BINARY_INSTALL_PATH)/; \
	);

.PHONY: clean
clean:
	@ ( \
		rm -rfv $(BIN); \
	);

