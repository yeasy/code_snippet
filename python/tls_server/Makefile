server:
	python3 server.py

client:
	python3 client.py

keys:
	openssl req -new -x509 -days 3650 -nodes -out client.pem -keyout client.key
	openssl req -new -x509 -days 3650 -nodes -out server.pem -keyout server.key