CC=gcc
CFLAG = -Wall
#CFLAG = -Wall -pedantic -ansi
#LDFLAGS=-lnsl -lm -lpthread -m32
SRCS=$(wildcard *.c)
OBJS=$(patsubst %.c,%.o, $(SRCS)) 
TARGET=$(patsubst %.c,%, $(SRCS))

all: $(TARGET)

%.o: %.c
	$(CC) -c $< -o $@ $(CFLAGS) 

%: %.o
	$(CC) $< -o $@ $(LDFLAGS)

test: $(TARGET)
	./server &
	./client 127.0.0.1 "[Client to Server] hello."
	killall server

clean:
	rm *.o $(TARGET) > /dev/null 2>&1 &
