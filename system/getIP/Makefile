#for kernel space
KERNELBUILD := /lib/modules/`uname -r`/build/
TARGET = test
obj-m := $(TARGET).o
$(TARGET)-objs := kgetSpecIP.o
#CFLAG = -Wall -pedantic -ansi
CFLAG = -Wall

default:user

#for kernel space
kernel: 
	@make -C $(KERNELBUILD) M=$(shell pwd) modules

insert: kernel
	sudo insmod $(TARGET).ko

remove:
	sudo rmmod $(TARGET).ko

#for user space
user: getSpecIP.o getAllIP
	cc -o getSpecIP $(CFLAG) getSpecIP.o
	cc -o getAllIP $(CFLAG) getAllIP.o

getSpecIP.o: getSpecIP.c
	cc -o getSpecIP.o $(CFLAG) -c getSpecIP.c

getAllIP.o: getAllIP.c
	cc -o getAllIP.o $(CFLAG) -c getAllIP.c

test: insert user
	./getSpecIP
	make remove

clean:
	rm getSpecIP getAllIP $(TARGET).mod.c *.o *.ko Module.symvers modules.order > /dev/null 2>&1 &
