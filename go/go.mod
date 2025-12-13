module github.com/FinamWeb/finam-trade-api/go

go 1.24.0

tool (
	github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-grpc-gateway
	github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-openapiv2
	google.golang.org/grpc/cmd/protoc-gen-go-grpc
	google.golang.org/protobuf/cmd/protoc-gen-go
)

require (
	github.com/grpc-ecosystem/grpc-gateway/v2 v2.27.3
	google.golang.org/genproto v0.0.0-20251111163417-95abcf5c77ba
	google.golang.org/genproto/googleapis/api v0.0.0-20251111163417-95abcf5c77ba
	google.golang.org/grpc v1.77.0
	google.golang.org/protobuf v1.36.10
)

require (
	github.com/kr/text v0.2.0 // indirect
	github.com/rogpeppe/go-internal v1.14.1 // indirect
	go.yaml.in/yaml/v3 v3.0.4 // indirect
	golang.org/x/net v0.47.0 // indirect
	golang.org/x/sys v0.38.0 // indirect
	golang.org/x/text v0.31.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20251111163417-95abcf5c77ba // indirect
	google.golang.org/grpc/cmd/protoc-gen-go-grpc v1.5.1 // indirect
)
