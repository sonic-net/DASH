CXXFLAGS_COMMON=
CXXFLAGS_COMMON+= -ansi
CXXFLAGS_COMMON+= -fPIC
CXXFLAGS_COMMON+= -pipe
CXXFLAGS_COMMON+= -std=c++11
CXXFLAGS_COMMON+= -Wall
CXXFLAGS_COMMON+= -Wcast-align
CXXFLAGS_COMMON+= -Wcast-qual
CXXFLAGS_COMMON+= -Wconversion
CXXFLAGS_COMMON+= -Wdisabled-optimization
CXXFLAGS_COMMON+= -Werror
CXXFLAGS_COMMON+= -Wextra
CXXFLAGS_COMMON+= -Wfloat-equal
CXXFLAGS_COMMON+= -Wformat=2
CXXFLAGS_COMMON+= -Wformat-nonliteral
CXXFLAGS_COMMON+= -Wformat-security
CXXFLAGS_COMMON+= -Wformat-y2k
CXXFLAGS_COMMON+= -Wimport
CXXFLAGS_COMMON+= -Winit-self
CXXFLAGS_COMMON+= -Wno-inline
CXXFLAGS_COMMON+= -Winvalid-pch
CXXFLAGS_COMMON+= -Wmissing-field-initializers
CXXFLAGS_COMMON+= -Wmissing-format-attribute
CXXFLAGS_COMMON+= -Wmissing-include-dirs
CXXFLAGS_COMMON+= -Wmissing-noreturn
CXXFLAGS_COMMON+= -Wno-aggregate-return
CXXFLAGS_COMMON+= -Wno-padded
CXXFLAGS_COMMON+= -Wno-switch-enum
CXXFLAGS_COMMON+= -Wno-unused-parameter
CXXFLAGS_COMMON+= -Wpacked
CXXFLAGS_COMMON+= -Wpointer-arith
CXXFLAGS_COMMON+= -Wredundant-decls
CXXFLAGS_COMMON+= -Wshadow
CXXFLAGS_COMMON+= -Wstack-protector
CXXFLAGS_COMMON+= -Wstrict-aliasing=3
CXXFLAGS_COMMON+= -Wswitch
CXXFLAGS_COMMON+= -Wswitch-default
CXXFLAGS_COMMON+= -Wunreachable-code
CXXFLAGS_COMMON+= -Wunused
CXXFLAGS_COMMON+= -Wvariadic-macros
CXXFLAGS_COMMON+= -Wwrite-strings
CXXFLAGS_COMMON+= -Wno-switch-default
CXXFLAGS_COMMON+= -Wconversion
CXXFLAGS_COMMON+= -Wno-psabi
CXXFLAGS_COMMON+= -Wno-unused-label

# Sources from OCP SAI Repo:
SAI_DIR=../SAI/meta/
SAI_INC=-I../SAI/meta -I../SAI/inc -I../SAI/experimental

SAI_OBJS=saimetadatautils.o saimetadata.o saiserialize.o
SAI_OBJS_PATHS=$(addprefix $(SAI_DIR)/,$(SAI_OBJS))

DASH_SAI_SRCS=$(wildcard *.cpp)
DASH_SAI_OBJS=$(DASH_SAI_SRCS:.cpp=.o)

all: libsai.so

%.d: %.cpp
	g++ $(SAI_INC) $(GXX_FLAGS) $(CXXFLAGS_COMMON) -M $^ -o $@

DEPS := $(DASH_SAI_OBJS:.o=.d)

-include $(DEPS)

%.o: %.cpp
	g++ $(SAI_INC) $(GXX_FLAGS) $(CXXFLAGS_COMMON) -MMD -c $< -o $@

libsai.so: $(SAI_OBJS_PATHS) $(DASH_SAI_OBJS)
	g++ -shared -g -o $@ $^

.PHONY: clean
clean:
	rm -f *.o libsai.so
