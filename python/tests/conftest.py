"""Shared pytest fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def anyio_backend() -> str:
    # pytest-asyncio uses asyncio; keep tests simple and consistent.
    return "asyncio"
