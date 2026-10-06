"""Unit tests for the screening rules."""

from app.filters import (
    extract_tvl_usd,
    passes_detail_filters,
    passes_market_filters,
    supplies_match,
)


def make_coin(**overrides):
    """Build a /coins/markets row that passes every market-level filter."""
    coin = {
        "market_cap": 1_000_000,
        "fully_diluted_valuation": 5_000_000,
        "total_volume": 100_000,
        "max_supply": 1_000_000_000,
        "total_supply": 1_000_000_000,
    }
    coin.update(overrides)
    return coin


def test_valid_coin_passes():
    """A coin meeting all market-level rules is kept."""
    assert passes_market_filters(make_coin())


def test_zero_market_cap_rejected():
    """Market cap must be strictly positive."""
    assert not passes_market_filters(make_coin(market_cap=0))


def test_fdv_limit():
    """FDV must be strictly below $100M and present."""
    assert not passes_market_filters(make_coin(fully_diluted_valuation=100_000_000))
    assert not passes_market_filters(make_coin(fully_diluted_valuation=None))


def test_volume_limit():
    """24h volume must be strictly above $50k."""
    assert not passes_market_filters(make_coin(total_volume=50_000))


def test_supply_rules():
    """Max supply must equal total supply, and both must be known."""
    assert supplies_match(10, 10)
    assert not supplies_match(10, 9)
    assert not supplies_match(None, None)


def test_tvl_extraction_and_detail_filters():
    """TVL is read from dict or number and combined with preview_listing."""
    detail = {
        "preview_listing": True,
        "market_data": {"total_value_locked": {"usd": 60_000}},
    }
    assert extract_tvl_usd(detail) == 60_000
    assert passes_detail_filters(detail)
    assert not passes_detail_filters({**detail, "preview_listing": False})
    low = {
        "preview_listing": True,
        "market_data": {"total_value_locked": {"usd": 50_000}},
    }
    assert not passes_detail_filters(low)
    none = {"preview_listing": True, "market_data": {"total_value_locked": None}}
    assert not passes_detail_filters(none)
