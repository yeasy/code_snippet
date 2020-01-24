#!/usr/bin/python3

import socket
import ssl
import time

host_addr = '144.25.32.206'
host_port = 8888
server_sni_hostname = 'example.com'
server_cert = 'server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

while True:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn = context.wrap_socket(s, server_side=False,
		                           server_hostname=server_sni_hostname)
		conn.connect((host_addr, host_port))
		if conn:
			print("SSL established. Peer: {}".format(conn.getpeercert()))
			print("Sending: 'Hello, world!")
			conn.send(b"Hello, world!")
			print("Closing connection")
			exit()
		conn.close()
		s.close()
	except Exception as e:
		print(e)
	time.sleep(3)
