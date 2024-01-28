IP=146.169.155.157
HOST=pi@$(IP)
DST=$(HOST):/home/pi
PASSWORD=asdfghjkl


.PHONY: send all

all:
	python src/main.py

run: send src/main.py
	sshpass -p $(PASSWORD) ssh $(HOST) -t "python main.py" 

send: src/main.py
	sshpass -p $(PASSWORD) scp src/* $(DST)

