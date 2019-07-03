#!/bin/sh

echo "Build plugin source code as .so file"
go build -buildmode=plugin -o plugin.so plugin.go

echo "Test load plugin and call methods"
go run main.go
