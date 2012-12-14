#for kernel space
KERNELBUILD := /lib/modules/`uname -r`/build/
TARGET = test
obj-m := $(TARGET).o
$(TARGET)-objs := main.o bf.o bf-gdt.o

default:user

kernel: 
	@make -C $(KERNELBUILD) M=$(shell pwd) modules

insert:
	sudo insmod $(TARGET).ko

remove:
	sudo rmmod $(TARGET).ko

#for user space
user: bf-gdt.o main.o bf.o
	cc -o bf-gdt -Wall -pedantic bf.o bf-gdt.o main.o

bf-gdt.o: bf-gdt.c bf-gdt.h
	cc -o bf-gdt.o -Wall -pedantic -ansi -c bf-gdt.c

bf.o: bf.c bf.h
	cc -o bf.o -Wall -pedantic -ansi -c bf.c

main.o: main.c bf-gdt.h
	cc -o main.o -Wall -pedantic -ansi -c main.c

test: user
	./bf-gdt

clean:
	rm bf-gdt $(TARGET).mod.c *.o *.ko Module.symvers modules.order *.d *.cmd > /dev/null 2>&1 &
