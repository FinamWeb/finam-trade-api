#!/usr/bin/env bash
# Generates Python gRPC stubs from the .proto files into finam_trade_api/proto/.
#
# Usage:
#   uv run ./scripts/generate_proto.sh
#
# Requirements:
#   uv sync
#
# mypy-protobuf installs two protoc plugins on PATH:
#   - protoc-gen-mypy       (typed stubs for proto messages, complements --pyi_out)
#   - protoc-gen-mypy_grpc  (typed stubs for gRPC service stubs — without this,
#                            grpc_python_out emits classes whose RPC methods are
#                            assigned dynamically in __init__ and are invisible
#                            to Pyright/Pylance/mypy. The .pyi makes them static.)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PYTHON_DIR/../.." && pwd)"

PROTO_ROOT="$REPO_ROOT/proto"
OUT_DIR="$PYTHON_DIR/finam_trade_api/proto"

if [ ! -d "$PROTO_ROOT/grpc/tradeapi/v1" ] || [ ! -d "$PROTO_ROOT/grpc/gateway" ]; then
    echo "ERROR: expected protobuf sources under $PROTO_ROOT/grpc" >&2
    exit 1
fi

# Collect every .proto file we need to compile (tradeapi + grpc-gateway helpers).
PROTO_FILES=()
while IFS= read -r proto_file; do
    PROTO_FILES+=("$proto_file")
done < <(
    find \
        "$PROTO_ROOT/grpc/tradeapi/v1" \
        "$PROTO_ROOT/grpc/gateway" \
        -name '*.proto' \
        -print |
        sort
)
if [ "${#PROTO_FILES[@]}" -eq 0 ]; then
    echo "ERROR: no protobuf sources found under $PROTO_ROOT/grpc" >&2
    exit 1
fi

# mypy-protobuf's plugins are external (not bundled with grpc_tools), so we
# pass them in via --plugin=. Using the absolute path keeps this working
# inside virtualenvs where the plugin lives under .venv/bin and is not
# necessarily on PATH for the python subprocess.
if ! PROTOC_GEN_MYPY="$(command -v protoc-gen-mypy)"; then
    PROTOC_GEN_MYPY=""
fi
if ! PROTOC_GEN_MYPY_GRPC="$(command -v protoc-gen-mypy_grpc)"; then
    PROTOC_GEN_MYPY_GRPC=""
fi
if [ -z "$PROTOC_GEN_MYPY" ] || [ -z "$PROTOC_GEN_MYPY_GRPC" ]; then
    echo "ERROR: mypy-protobuf is not installed. Run: uv sync" >&2
    exit 1
fi

BUILD_DIR="$(mktemp -d "$PYTHON_DIR/finam_trade_api/.proto-build.XXXXXX")"
cleanup() {
    if [ -n "${BUILD_DIR:-}" ] && [ -d "$BUILD_DIR" ]; then
        rm -rf -- "$BUILD_DIR"
    fi
}
trap cleanup EXIT

python -m grpc_tools.protoc \
    --proto_path="$PROTO_ROOT" \
    --plugin=protoc-gen-mypy="$PROTOC_GEN_MYPY" \
    --plugin=protoc-gen-mypy_grpc="$PROTOC_GEN_MYPY_GRPC" \
    --python_out="$BUILD_DIR" \
    --grpc_python_out="$BUILD_DIR" \
    --mypy_out="$BUILD_DIR" \
    --mypy_grpc_out="$BUILD_DIR" \
    "${PROTO_FILES[@]}"

# Create __init__.py files at every package level so the generated modules
# are importable as finam_trade_api.proto.grpc.tradeapi.v1.<service>.
find "$BUILD_DIR" -type d -exec touch {}/__init__.py \;

# protoc emits absolute Python imports rooted at the proto path
# (e.g. ``from grpc.tradeapi.v1.accounts import accounts_service_pb2``),
# which collide with the real ``grpc`` package and don't resolve under
# ``finam_trade_api.proto``. Rewrite them to be relative to this package.
#
# We target only the two top-level proto roots that exist in this repo so
# we don't accidentally mangle unrelated imports (e.g. ``google.protobuf``,
# which is provided by the protobuf runtime and must stay absolute).
python "$SCRIPT_DIR/_fix_proto_imports.py" "$BUILD_DIR"

# Sanity check: any remaining ``from grpc.<root>`` import that *isn't* prefixed
# with finam_trade_api.proto means the rewriter missed a top-level proto root
# we forgot to register in _fix_proto_imports.py — that will explode at import
# time with a ModuleNotFoundError. Fail the build now with a clear message
# instead.
LEAKED=$(grep -rEn '^(from|import) grpc\.[a-zA-Z_]' "$BUILD_DIR" \
    --include='*.py' --include='*.pyi' \
    | grep -v 'finam_trade_api\.proto\.grpc\.' || true)
if [ -n "$LEAKED" ]; then
    echo "ERROR: generated stubs still reference unrewritten 'grpc.<root>' imports:" >&2
    echo "$LEAKED" >&2
    echo "Add the missing root to ROOTS_TO_REWRITE in scripts/_fix_proto_imports.py." >&2
    exit 1
fi

# Replace the prior output only after every generation and validation step has
# succeeded, so a missing tool or invalid proto cannot destroy a usable SDK.
rm -rf -- "$OUT_DIR"
mv -- "$BUILD_DIR" "$OUT_DIR"
trap - EXIT

echo "Generated Python stubs in $OUT_DIR"
