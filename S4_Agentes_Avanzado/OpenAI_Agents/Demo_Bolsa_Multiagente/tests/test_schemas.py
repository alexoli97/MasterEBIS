from src.schemas import Horizon, Mandate, RiskProfile


def test_mandate_defaults():
    m = Mandate(
        market_situation="x",
        mandate="y",
        amount=10000,
        horizon=Horizon.LONG,
    )
    assert m.risk_profile == RiskProfile.BALANCED
    assert m.base_currency == "EUR"


def test_mandate_amount_positive():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Mandate(market_situation="x", mandate="y", amount=0, horizon=Horizon.LONG)
