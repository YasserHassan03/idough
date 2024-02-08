IP=146.169.154.110
HOST=pi@$(IP)
DST=$(HOST):/home/pi
PASSWORD=asdfghjkl


.PHONY: send all cleanssh

all: send src/main.py
	sshpass -p $(PASSWORD) ssh $(HOST) -t "python main.py" 

cleanssh: 
	rm -rf ~omar/.ssh/knownhosts*
	ssh $(HOST)


send: src/main.py
	sshpass -p $(PASSWORD) scp src/* $(DST)

