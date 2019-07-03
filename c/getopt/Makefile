# This is a Makefile template.
# Feel free to distribute or modify the code.:)
# Version: 0.2
# Author: Baohua Yang@THU
# Created: Sep 1, 2008
# Updated: May 31, 2011

CC=gcc
INCLUDES=-I./
CFLAGS=$(INCLUDES) -O2 -Wall -g -m32
LDFLAGS=-lnsl -lm -lpthread -m32
SRCS=$(wildcard *.c)
OBJS=$(patsubst %.c,%.o, $(SRCS)) 
DEPS=$(patsubst %.c,%.d, $(SRCS))
RM=rm -f

#change this line, set your destination prog.
TARGET=$(patsubst %.c,%, $(SRCS)) 

all: $(DEPS) $(TARGET)
#all:$(TARGET)

################ below needs no change in most case ################

test: $(TARGET)
	for i in [$(TARGET)]; do \
	./$(i)\
	done;

$(TARGET): $(OBJS)
	$(CC) -o $(TARGET) $(OBJS) $(LDFLAGS)

%.o: %.c
	$(CC) -c $< -o $@ $(CFLAGS) 

%: %.o
	$(CC) $< -o $@ $(LDFLAGS)

%.d: %.c
	$(CC) -MM $(CFLAGS) $< >$@.$$$$;\
	sed 's,\($*\)\.o[ :]*,\1.o $@: ,g' < $@.$$$$ > $@;\
	$(RM) $@.$$$$;

.PHONY : clean
clean: 
	$(RM) $(TARGET) *.o *.bak *.c~ *.h~ *.d
