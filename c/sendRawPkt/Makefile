TARGET = sendRawPkt

$(TARGET): $(TARGET).c
	gcc -o $(TARGET) $(TARGET).c

test: $(TARGET)
	#sudo tcpdump -nettti eth0 '(ether dst host 00:11:22:33:44:55)'& 
	sudo ./$(TARGET) eth0

clean:
	@rm $(TARGET) *.o >/dev/null 2>&1 &
