#!/usr/bin/python3

import socket
from socket import AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR
import ssl

listen_addr = '0.0.0.0'
listen_port = 12001
server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)

bindsocket = socket.socket()
bindsocket.bind((listen_addr, listen_port))
bindsocket.listen(5)

while True:
    try:
        print("Waiting for client")
        newsocket, fromaddr = bindsocket.accept()
        print("Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
        conn = context.wrap_socket(newsocket, server_side=True)
        print("SSL established. Peer: {}".format(conn.getpeercert()))
        buf = b''  # Buffer to hold received client data
        try:
            while True:
                data = conn.recv(4096)
                if data:
                    # Client sent us data. Append to buffer
                    buf += data
                else:
                    # No more data from client. Show buffer and close connection.
                    print("Received:", buf)
                    break
        finally:
            print("Closing connection")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
    except ssl.SSLEOFError as e:
        print(e)
    finally:
        print("Something wrong is received")
