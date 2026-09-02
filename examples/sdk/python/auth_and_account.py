"""Authenticate and fetch the first available account."""

from __future__ import annotations

import os

from finam_trade_api import FinamClient
from finam_trade_api.accounts import GetAccountRequest
from finam_trade_api.auth_messages import TokenDetailsRequest


def main() -> None:
    secret = os.environ["TRADE_API_SECRET"]

    with FinamClient(secret=secret) as client:
        token = client.get_token()
        if token is None:
            raise RuntimeError("authentication did not return a token")

        details = client.auth.TokenDetails(TokenDetailsRequest(token=token))
        account_ids = list(details.account_ids)
        print("Available account IDs:", account_ids)

        if not account_ids:
            print("Authentication succeeded; this secret exposes no trading accounts.")
            return

        account = client.accounts.GetAccount(GetAccountRequest(account_id=account_ids[0]))
        print("First account:", account)


if __name__ == "__main__":
    main()
