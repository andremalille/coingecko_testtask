"""Pure filtering rules for the crypto screener."""

import math
from typing import Any

MIN_MARKET_CAP = 0
MAX_FDV = 100_000_000
MIN_VOLUME_24H = 50_000
MIN_TVL = 50_000


def _number(value: Any) -> float | None:
    """Return ``value`` as a float, or None if it is missing or not numeric."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def supplies_match(max_supply: Any, total_supply: Any) -> bool:
    """Return True when both supplies are known, positive and equal."""
    max_s, total_s = _number(max_supply), _number(total_supply)
    if max_s is None or total_s is None or max_s <= 0 or total_s <= 0:
        return False
    return math.isclose(max_s, total_s, rel_tol=1e-9)


def passes_market_filters(coin: dict[str, Any]) -> bool:
    """Apply the filters that only need a ``/coins/markets`` row."""
    mcap = _number(coin.get("market_cap"))
    fdv = _number(coin.get("fully_diluted_valuation"))
    volume = _number(coin.get("total_volume"))
    if mcap is None or mcap <= MIN_MARKET_CAP:
        return False
    if fdv is None or fdv >= MAX_FDV:
        return False
    if volume is None or volume <= MIN_VOLUME_24H:
        return False
    return supplies_match(coin.get("max_supply"), coin.get("total_supply"))


def extract_tvl_usd(detail: dict[str, Any]) -> float | None:
    """Extract TVL in USD from a ``/coins/{id}`` payload."""
    market_data = detail.get("market_data") or {}
    tvl = market_data.get("total_value_locked")
    if isinstance(tvl, dict):
        return _number(tvl.get("usd"))
    return _number(tvl)


def passes_tvl_filter(detail: dict[str, Any]) -> bool:
    """Return True when the coin's TVL is known and above 50k USD."""
    tvl = extract_tvl_usd(detail)
    return tvl is not None and tvl > MIN_TVL


def passes_detail_filters(detail: dict[str, Any]) -> bool:
    """Apply all filters that need a ``/coins/{id}`` payload."""
    return detail.get("preview_listing") is True and passes_tvl_filter(detail)
