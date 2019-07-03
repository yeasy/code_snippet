CC=gcc
CFLAGS = -O2 -Wall -pedantic -lpthread
#CFLAG = -Wall

SRCS=$(wildcard *.c)
OBJS=$(patsubst %.c,%.o, $(SRCS)) 

TARGET = main

all:$(TARGET)

$(TARGET): $(OBJS)
	cc -o $(TARGET) $(CFLAGS) $(OBJS)

%.o: %.c
	$(CC) -c $< -o $@ $(CFLAGS) 

test: $(TARGET)
	./$(TARGET) -g 239.0.0.1 -p 5000 -t 1 -c "payload here" #ip, port, interval, content

clean:
	rm $(TARGET) $(OBJS) > /dev/null 2>&1 &
