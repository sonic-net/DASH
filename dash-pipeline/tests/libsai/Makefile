# Call make in each subdirectory
.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e
SUBDIRS := $(wildcard */.)


define FOREACH
    for DIR in $(SUBDIRS); do \
        $(MAKE) -C $$DIR $(1); \
    done
endef

all: $(SUBDIRS)
	$(call FOREACH,all)


clean: $(SUBDIRS)
	$(call FOREACH,clean)


.PHONY: all $(SUBDIRS)
