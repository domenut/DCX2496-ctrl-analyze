# Automatic Makefile for multiple languages
# Chris McDonnell Oct/2022 

.POSIX:
.PHONY: run clean


C_SRCS = \
src/impulse.c


CXX_SRCS = \
src/spectrum.cpp


PROG = spectrum.out
BUILDIR = build

C_OPTIM= -O2 -march=native
C_OPTIM+= -DNDEBUG 
CXX_OPTIM= -O2 -march=native
# CXX_OPTIM= -O0 -march=native
CXX_OPTIM+= -DNDEBUG
# PROFILNG= -pg

# CPPFLAGS+= -I

# CFLAGS+= $(C_OPTIM) -DVERSION=\"$(VERSION)\" -std=gnu99 $(gsl-config --cflags)
CFLAGS+= $(C_OPTIM) -DVERSION=\"$(VERSION)\" -std=gnu11 $(gsl-config --cflags)
CFLAGS+= -I./src  
CFLAGS+= -Wall -Wextra

# CFLAGS+= -pedantic-errors 
CFLAGS+= -Wno-unused -Wno-unused-function -Wno-unused-parameter

# CXXFLAGS+= $(CXX_OPTIM) -DHAVE_SEMAPHORE -std=c++2a -march=native
CXXFLAGS+= $(CXX_OPTIM) -DHAVE_SEMAPHORE -std=gnu++2a -march=native
CXXFLAGS+= -Wall -Wextra -I./src
CXXFLAGS+= -pedantic-errors
CXXFLAGS+= -Wno-unused -Wno-unused-function -Wno-unused-parameter

LDFLAGS+= -I./src -L/usr/X11/lib
LDLIBS+= -ljack -lm -lz -lpthread -latomic -lfftw3f $(gsl-config --libs)

F_SRCS = 
FC_FLAGS =

# SHLIB_CMP_FLAGS = -fPIC
# SHLIB_LD_FLAGS = -shared
################ Hopefully automatic. ( except objdump ) ####################
CXX = g++
CC = gcc
FC = fortran-10

C_OBJS = $(addprefix $(BUILDIR)/, $(notdir $(C_SRCS:.c=.o)) )
CXX_OBJS = $(addprefix $(BUILDIR)/, $(notdir $(CXX_SRCS:.cpp=.o)) )
F_OBJS = $(addprefix $(BUILDIR)/, $(notdir $(F_SRCS:.F=.o)) )

# all: $(CXX_OBJS) $(C_OBJS) objdump
# all: $(CXX_OBJS) $(C_OBJS) run
all: $(BUILDIR)/$(PROG) 


$(BUILDIR)/$(PROG): $(CXX_OBJS) $(C_OBJS)
	$(CXX) $(PROFILNG) $(SHLIB_LD_FLAGS) -o '$@' $^ $(LDFLAGS) $(LDLIBS)

# $(BUILDIR)/$(PROG): $(CXX_OBJS) $(C_OBJS)
# 	$(CXX) $(PROFILNG) -o '$@' $^ $(LDFLAGS) $(LDLIBS)

$(C_OBJS): %.o: $(C_SRCS)
	$(CC) $(PROFILNG) $(SHLIB_CMP_FLAGS) -c  $(CFLAGS) $(CPPFLAGS) $?
	mv *.o $(BUILDIR)

$(CXX_OBJS): %.o: $(CXX_SRCS)
	$(CXX) $(PROFILNG) $(SHLIB_CMP_FLAGS) -c $(CXXFLAGS) $(CPPFLAGS) $?
	mv *.o $(BUILDIR)

$(F_OBJS): %.o: $(F_SRCS)
	$(FC) -c $(F_FLAGS) $?
	mv *.o $(BUILDIR)


run: $(BUILDIR)/$(SHLIB)
	$(BUILDIR)/$(SHLIB)

clean:
	rm -f *.o *.out $(C_OBJS) $(CXX_OBJS) $(BUILDIR)/*.out $(BUILDIR)/*.so $(BUILDIR)/*.s


objdump: $(BUILDIR)/spectrum.o
	objdump -dS -M intel $(BUILDIR)/spectrum.o > $(BUILDIR)/spectrum_objdmp.s
# 	objdump -dS -M intel $(BUILDIR)/main.o --visualize-jumps=extended-color

##############################################################
# General GCC notes...
# Shared library example command
# g++ -Wall -shared -fPIC -o ~/libs/libmylibrary.so libmylibrary.cpp
##############################################################

# $(BUILDIR)/gnuplot.o: src/gnuplot.c
# 	gcc -c -g $(CFLAGS) -o '$@' '$<'
# 
# $(BUILDIR)/gnuplot_i.o: src/gnuplot_i.c
# 	gcc -c -g $(CFLAGS) -o '$@' '$<'
# 
# $(BUILDIR)/impulse.o: src/impulse.c
# 	gcc -c -g $(CFLAGS) -o '$@' '$<'



### Assembly output
# g++ -fno-asynchronous-unwind-tables -fno-exceptions -fno-rtti -fverbose-asm \
#     -Wall -Wextra  foo.cpp   -O3 -masm=intel -S -o- | less

# or...
# g++ -g -O3 -std=c++14 -c example.cpp -o example.o && objdump -dS -M intel example.o > example.ObjAssy



