# etherbridge - Makefile


CC=gcc
INCLUDES=-I./ -I/usr/include
CFLAGS=$(INCLUDES) -O2 -Wall -g
LDFLAGS=-L/usr/lib -lpcap -lnsl -lm -lpthread
SRCS=$(wildcard *.c)
#SRCS=source.c
OBJS=$(patsubst %.c,%.o, $(SRCS)) 
DEPS=$(patsubst %.c,%.d, $(SRCS))
TARGET=etherbridge
RM=rm -f
INSTALL_DIR = /usr/bin

all: $(DEPS) $(TARGET)
	#all:$(TARGET)

################ below needs no change in most case ################

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

.PHONY : clean install uninstall
	clean: 
	$(RM) $(TARGET) *.o *.bak *.c~ *.h~ *.d

install:
	cp -f $(TARGET) $(INSTALL_DIR)/
uninstall:
	rm -f $(INSTALL_DIR)/$(TARGET)


CC = gcc
INCLUDE = -I/usr/include
LIBS = -L/usr/lib -lpcap -lpthread
INSTALL_DIR = /usr/bin

all: 
	$(CC) etherbridge.c headers.c -o etherbridge $(INCLUDE) $(LIBS)


clean:
	rm -f $(INSTALL_DIR)/etherbridge

