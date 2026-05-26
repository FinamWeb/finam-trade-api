#!/usr/bin/env bash
# Generates Python gRPC stubs from the .proto files into finam_trade_api/proto/.
#
# Usage:
#   ./scripts/generate_proto.sh
#
# Requirements:
#   pip install grpcio-tools mypy-protobuf
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
REPO_ROOT="$(cd "$PYTHON_DIR/.." && pwd)"

PROTO_ROOT="$REPO_ROOT/proto"
OUT_DIR="$PYTHON_DIR/finam_trade_api/proto"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# Collect every .proto file we need to compile (tradeapi + grpc-gateway helpers).
mapfile -t PROTO_FILES < <(find \
    "$PROTO_ROOT/grpc/tradeapi/v1" \
    "$PROTO_ROOT/grpc/gateway" \
    -name '*.proto')

# mypy-protobuf's plugins are external (not bundled with grpc_tools), so we
# pass them in via --plugin=. Using the absolute path keeps this working
# inside virtualenvs where the plugin lives under .venv/bin and is not
# necessarily on PATH for the python subprocess.
PROTOC_GEN_MYPY="$(command -v protoc-gen-mypy)"
PROTOC_GEN_MYPY_GRPC="$(command -v protoc-gen-mypy_grpc)"
if [ -z "$PROTOC_GEN_MYPY" ] || [ -z "$PROTOC_GEN_MYPY_GRPC" ]; then
    echo "ERROR: mypy-protobuf is not installed. Run: pip install mypy-protobuf" >&2
    exit 1
fi

python -m grpc_tools.protoc \
    --proto_path="$PROTO_ROOT" \
    --plugin=protoc-gen-mypy="$PROTOC_GEN_MYPY" \
    --plugin=protoc-gen-mypy_grpc="$PROTOC_GEN_MYPY_GRPC" \
    --python_out="$OUT_DIR" \
    --grpc_python_out="$OUT_DIR" \
    --mypy_out="$OUT_DIR" \
    --mypy_grpc_out="$OUT_DIR" \
    "${PROTO_FILES[@]}"

# Create __init__.py files at every package level so the generated modules
# are importable as finam_trade_api.proto.grpc.tradeapi.v1.<service>.
find "$OUT_DIR" -type d -exec touch {}/__init__.py \;

# protoc emits absolute Python imports rooted at the proto path
# (e.g. ``from grpc.tradeapi.v1.accounts import accounts_service_pb2``),
# which collide with the real ``grpc`` package and don't resolve under
# ``finam_trade_api.proto``. Rewrite them to be relative to this package.
#
# We target only the two top-level proto roots that exist in this repo so
# we don't accidentally mangle unrelated imports (e.g. ``google.protobuf``,
# which is provided by the protobuf runtime and must stay absolute).
python "$SCRIPT_DIR/_fix_proto_imports.py" "$OUT_DIR"

# Sanity check: any remaining ``from grpc.<root>`` import that *isn't* prefixed
# with finam_trade_api.proto means the rewriter missed a top-level proto root
# we forgot to register in _fix_proto_imports.py — that will explode at import
# time with a ModuleNotFoundError. Fail the build now with a clear message
# instead.
LEAKED=$(grep -rEn '^(from|import) grpc\.[a-zA-Z_]' "$OUT_DIR" \
    --include='*.py' --include='*.pyi' \
    | grep -v 'finam_trade_api\.proto\.grpc\.' || true)
if [ -n "$LEAKED" ]; then
    echo "ERROR: generated stubs still reference unrewritten 'grpc.<root>' imports:" >&2
    echo "$LEAKED" >&2
    echo "Add the missing root to ROOTS_TO_REWRITE in scripts/_fix_proto_imports.py." >&2
    exit 1
fi

echo "Generated Python stubs in $OUT_DIR"
