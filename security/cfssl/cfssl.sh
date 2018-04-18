#!/usr/bin/env bash

echo "CFSSL: https://github.com/cloudflare/cfssl"

echo "Clean existing generated files"
rm -f ca.csr ca.pem ca-key.pem
rm -f test.csr test.pem test-key.pem

if ! command -v cfssl >/dev/null 2>&1; then
	echo "Installing (Need have golang env first)"
	go get -u github.com/cloudflare/cfssl/cmd/...
fi

if [ ! -f ca.pem ]; then
	echo "Generate self-sign cert for the ca"
	cfssl genkey -initca ca-csr.json | cfssljson -bare ca
fi

echo "Generate signed cert for test identity"
cfssl gencert \
	-config signing-profiles.json \
	-profile client \
	-ca ca.pem \
	-ca-key ca-key.pem \
	test-csr.json | cfssljson -bare test
