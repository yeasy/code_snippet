proto:
	protoc --go_out=plugins=grpc:. ./hello/*.proto
server:
	# GOPATH=$(PWD)/../../ 
	go run server/server.go
client:
	# GOPATH=$(PWD)/../../ 
	go run client/client.go

.PHONY: all proto server client test
