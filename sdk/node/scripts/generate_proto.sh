#!/usr/bin/env bash
# Generate typed TypeScript messages and nice-grpc service definitions.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$NODE_DIR/../.." && pwd)"
PROTO_ROOT="$REPO_ROOT/proto"
OUT_DIR="$NODE_DIR/src/generated"
BUILD_DIR="$(mktemp -d "$NODE_DIR/.proto-build.XXXXXX")"

cleanup() {
  if [ -d "$BUILD_DIR" ]; then
    rm -rf -- "$BUILD_DIR"
  fi
}
trap cleanup EXIT

PROTO_FILES=()
while IFS= read -r proto_file; do
  PROTO_FILES+=("$proto_file")
done < <(
  find "$PROTO_ROOT/grpc/tradeapi/v1" -name '*.proto' -print | sort
)
PROTO_FILES+=(
  "$PROTO_ROOT/google/protobuf/timestamp.proto"
  "$PROTO_ROOT/google/protobuf/wrappers.proto"
  "$PROTO_ROOT/google/type/date.proto"
  "$PROTO_ROOT/google/type/decimal.proto"
  "$PROTO_ROOT/google/type/interval.proto"
  "$PROTO_ROOT/google/type/money.proto"
)

"$NODE_DIR/node_modules/.bin/grpc_tools_node_protoc" \
  --proto_path="$PROTO_ROOT" \
  --plugin=protoc-gen-ts_proto="$NODE_DIR/node_modules/.bin/protoc-gen-ts_proto" \
  --ts_proto_out="$BUILD_DIR" \
  --ts_proto_opt=esModuleInterop=true \
  --ts_proto_opt=emitImportedFiles=false \
  --ts_proto_opt=forceLong=bigint \
  --ts_proto_opt=importSuffix=.js \
  --ts_proto_opt=outputServices=nice-grpc \
  --ts_proto_opt=outputServices=generic-definitions \
  --ts_proto_opt=useExactTypes=false \
  "${PROTO_FILES[@]}"

rm -rf -- "$OUT_DIR"
mv -- "$BUILD_DIR" "$OUT_DIR"
trap - EXIT

echo "Generated TypeScript stubs in $OUT_DIR"
