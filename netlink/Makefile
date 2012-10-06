#for kernel space
KERNELBUILD := /lib/modules/`uname -r`/build/
TARGET = test
obj-m := $(TARGET).o
$(TARGET)-objs := gnKernel.o
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
user: gnUser.o
	cc -o gnUser $(CFLAG) gnUser.o

gnUser.o: gnUser.c
	cc -o gnUser.o $(CFLAG) -c gnUser.c

test: insert user
	./gnUser
	make remove

clean:
	rm gnUser $(TARGET).mod.c *.o *.ko Module.symvers modules.order > /dev/null 2>&1 &
