"""Verify that Python release archives contain the SDK's runtime files."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from collections.abc import Iterable
from pathlib import Path

REQUIRED_SUFFIXES = (
    "finam_trade_api/__init__.py",
    "finam_trade_api/py.typed",
    ("finam_trade_api/proto/grpc/tradeapi/v1/marketdata/marketdata_service_pb2.py"),
    ("finam_trade_api/proto/grpc/tradeapi/v1/marketdata/marketdata_service_pb2_grpc.py"),
)
EXPECTED_ARCHIVE_PREFIX = "finam_sdk-"


def _archive_names(path: Path) -> Iterable[str]:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            yield from archive.namelist()
        return

    if path.name.endswith(".tar.gz"):
        with tarfile.open(path, "r:gz") as archive:
            yield from archive.getnames()
        return

    raise ValueError(f"unsupported distribution archive: {path}")


def _verify(path: Path) -> None:
    if not path.name.startswith(EXPECTED_ARCHIVE_PREFIX):
        raise RuntimeError(
            f"{path.name} does not use the expected distribution name {EXPECTED_ARCHIVE_PREFIX}"
        )
    names = tuple(_archive_names(path))
    missing = [
        suffix for suffix in REQUIRED_SUFFIXES if not any(name.endswith(suffix) for name in names)
    ]
    if missing:
        joined = "\n  - ".join(missing)
        raise RuntimeError(f"{path.name} is missing runtime files:\n  - {joined}")
    print(f"Verified {path.name}")


def main() -> None:
    dist_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    archives = sorted((*dist_dir.glob("*.whl"), *dist_dir.glob("*.tar.gz")))
    wheels = [path for path in archives if path.suffix == ".whl"]
    source_distributions = [path for path in archives if path.name.endswith(".tar.gz")]
    if len(wheels) != 1 or len(source_distributions) != 1:
        raise RuntimeError(
            f"expected one wheel and one source distribution in {dist_dir}; "
            f"found {len(wheels)} wheel(s) and "
            f"{len(source_distributions)} source distribution(s)"
        )
    for archive in archives:
        _verify(archive)


if __name__ == "__main__":
    main()
