from custom_components.anwb_energie.sensor import _hourly_attrs


def test_hourly_attrs_preserves_missing_prices_when_converting_to_euros() -> None:
    result = _hourly_attrs(
        {
            "hourly": {
                "2026-09-27T10:00:00+02:00": {
                    "market_price": 20,
                    "all_in_price": None,
                }
            }
        },
        use_euros=True,
    )

    assert result["hourly_prices"]["2026-09-27T10:00:00+02:00"] == {
        "market_price": 0.2,
        "all_in_price": None,
    }