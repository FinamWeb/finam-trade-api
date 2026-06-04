"""Authenticate and fetch account info.

Usage:
    FINAM_SECRET=... FINAM_ACCOUNT_ID=... python examples/auth_and_account.py
"""

from __future__ import annotations

import os

from finam_trade_api import FinamClient
from finam_trade_api.accounts import GetAccountRequest


def main() -> None:
    secret = os.environ["FINAM_SECRET"]
    account_id = os.environ["FINAM_ACCOUNT_ID"]

    with FinamClient(secret=secret) as client:
        # JWT was already fetched during construction; get_token() returns
        # the current cached snapshot without blocking.
        token = client.get_token() or ""
        print(f"JWT (truncated): {token[:32]}...")

        account = client.accounts.GetAccount(GetAccountRequest(account_id=account_id))
        print(account)


if __name__ == "__main__":
    main()
