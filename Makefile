BIN := bin
BINFILE := $(BIN)/chopper
PYXFILE := $(BIN)/chopper.pyx
CFILE := $(BIN)/chopper.c
CFLAGS := -Os -I /usr/include/python3.6m -lpython3.6m -lpthread -lm -lutil -ldl

.PHONY: all
all: binary

.PHONY: binary
binary: c
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
		find src/chopper -type f -name \*.py -not -name __init__.py -exec cat {} > $(PYXFILE) \; ; \
		cat src/main.py >> $(PYXFILE); \
		sed -i '/^from\ \./d; /^from\ chopper/g' $(PYXFILE); \
	);

.PHONY: clean
clean:
	@ ( \
		rm -rfv $(BIN); \
	);

