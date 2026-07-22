"""The strategy-facing namespace stays small and brand-neutral."""

from finam_trade_api import FinamClient
from finam_trade_api.market_data import Bar as SdkBar
from trade_api import Bar, Client


def test_neutral_facade_reexports_sdk_types() -> None:
    assert Client is FinamClient
    assert Bar is SdkBar
