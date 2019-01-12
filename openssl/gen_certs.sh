#!/bin/bash

echo "===Generate a self signed certificate as the CA"
[ -f ca.crt ] || openssl req -nodes -newkey rsa:2048 -subj "/C=US/ST=State/L=Location/O=OrgName/OU=IT Department/CN=ca" -keyout ca.key -x509 -days 365 -out ca.crt

#echo "Review genrated certificate"
#openssl x509 -text -noout -in ca.crt

echo "===Generate private key for server"
#[ -f server.key ] || openssl genrsa -nodes -out server.key 2048
[ -f server.key ] || openssl req -nodes -newkey rsa:2048 -subj "/C=US/ST=State/L=Location/O=OrgName/OU=IT Department/CN=server" -x509 -keyout server.key
#[ -f server.key ] || openssl req -newkey rsa:2048 -subj "/C=US/ST=State/L=Location/O=OrgName/OU=IT Department/CN=server" -nodes -keyout server.key -x509 -days 365 -out server-tmp.crt

# Optionally inspect the generated private key
# openssl rsa -in ca.key -noout -text

# Optionally inspect the generated public key
# openssl rsa -in example.org.pubkey -pubin -noout -text

#echo "Generate private key and csr for server: use server address as CN field (can use wildcard)"
#openssl req -new -key server.key -out server.csr

echo "===Generate the config file for the server csr, indicating server key file"
if [ ! -f server-csr.conf ] ; then
cat <<EOF >./server-csr.conf
[ req ]
prompt = no
default_bits = 2048
default_keyfile = server.key
distinguished_name = req_distinguished_name
req_extensions = req_ext

[ req_distinguished_name ]
C=CN
ST=BJ
L=BJ
O=O
OU=O
CN=server

[ req_ext ]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = server
DNS.3 = oci-lbr
IP.1 = 127.0.0.1
IP.2 = 129.213.9.145
IP.3 = 129.213.62.129
IP.4 = 129.213.53.75
IP.5 = 129.213.51.73
EOF
fi

echo "===Generate csr based on the config"
[ -f server.csr ] || openssl req -new -nodes -out server.csr -config server-csr.conf

echo "===Sign a server certificate based on csr by CA"
[ -f server.crt ] || openssl x509 -req -in server.csr -extfile v3.ext -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt

echo "===Combine key and cert together as server certificate"
if [ ! -f server.pem ]; then
  cp server.key server.pem
  cat server.crt >> server.pem
fi
