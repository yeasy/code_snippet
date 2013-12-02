# etherbridge - Makefile

CC = gcc
INCLUDE = -I/usr/include
LIBS = -L/usr/lib -lpcap -lpthread
INSTALL_DIR = /usr/bin

all: 
	$(CC) etherbridge.c -o etherbridge $(INCLUDE) $(LIBS)
	
install:
	cp -f etherbridge $(INSTALL_DIR)/etherbridge
	
clean:
	rm -f $(INSTALL_DIR)/etherbridge
	
