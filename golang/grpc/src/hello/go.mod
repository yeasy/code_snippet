module hello

go 1.13

require (
	github.com/golang/protobuf v1.5.3
	golang.org/x/net v0.17.0
	google.golang.org/grpc v1.56.3
)

replace hello/hello => ./hello
