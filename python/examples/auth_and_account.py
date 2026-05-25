"""Authenticate and fetch account info.

Usage:
    FINAM_SECRET=... FINAM_ACCOUNT_ID=... python examples/auth_and_account.py
"""

from __future__ import annotations

import os

from finam_trade_api import FinamClient
from finam_trade_api.proto.grpc.tradeapi.v1.accounts.accounts_service_pb2 import (
    GetAccountRequest,
)


def main() -> None:
    secret = os.environ["FINAM_SECRET"]
    account_id = os.environ["FINAM_ACCOUNT_ID"]

    with FinamClient(secret=secret) as client:
        # JWT was already fetched during construction.
        print(f"JWT (truncated): {client.token[:32]}...")

        account = client.accounts.GetAccount(GetAccountRequest(account_id=account_id))
        print(account)


if __name__ == "__main__":
    main()
