"""Rewrite imports in protoc-generated .py / .pyi files to be relative to
``finam_trade_api.proto``.

protoc emits absolute imports rooted at the proto path, e.g.::

    from grpc.tradeapi.v1.accounts import accounts_service_pb2 as ...

That collides with the real ``grpc`` runtime package (the gRPC client) and
doesn't resolve when these stubs live inside ``finam_trade_api/proto/``.
We rewrite the two repo-specific roots to point back into the package,
leaving ``google.*`` and other absolute imports alone (those resolve via
the protobuf / googleapis-common-protos runtimes).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOTS_TO_REWRITE = ("grpc.tradeapi", "grpc.gateway")

PACKAGE_PREFIX = "finam_trade_api.proto."

# Matches both `import X.Y.Z` and `from X.Y.Z import name` where X.Y.Z starts
# with one of our roots.
_ROOTS_ALT = "|".join(re.escape(r) for r in ROOTS_TO_REWRITE)
PATTERNS = [
    (
        re.compile(rf"^(from\s+)({_ROOTS_ALT})(\.[\w.]*)?(\s+import\s+)", re.MULTILINE),
        rf"\1{PACKAGE_PREFIX}\2\3\4",
    ),
    (
        re.compile(rf"^(import\s+)({_ROOTS_ALT})(\.[\w.]*)?(\s|$)", re.MULTILINE),
        rf"\1{PACKAGE_PREFIX}\2\3\4",
    ),
]


def rewrite_file(path: Path) -> bool:
    text = path.read_text()
    new_text = text
    for pattern, replacement in PATTERNS:
        new_text = pattern.sub(replacement, new_text)
    if new_text != text:
        path.write_text(new_text)
        return True
    return False


def main() -> None:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <out_dir>", file=sys.stderr)
        raise SystemExit(2)
    out_dir = Path(sys.argv[1])
    changed = 0
    for ext in ("*.py", "*.pyi"):
        for f in out_dir.rglob(ext):
            if rewrite_file(f):
                changed += 1
    print(f"Rewrote imports in {changed} file(s)")


if __name__ == "__main__":
    main()
