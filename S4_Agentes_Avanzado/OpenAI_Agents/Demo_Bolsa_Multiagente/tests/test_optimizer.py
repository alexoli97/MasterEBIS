"""Smoke test optimizer. Skipped offline."""
import pytest

from src.schemas import Horizon, Mandate, RiskProfile


@pytest.mark.network
def test_optimizer_smoke():
    from src.tools.optimizer import optimize
    m = Mandate(
        market_situation="test",
        mandate="test",
        amount=10000,
        horizon=Horizon.LONG,
        risk_profile=RiskProfile.BALANCED,
    )
    pf = optimize(["AAPL", "MSFT", "GOOGL", "BRK-B", "JNJ"], m)
    assert len(pf.holdings) >= 2
    assert abs(sum(h.weight for h in pf.holdings) + pf.cash_weight - 1.0) < 0.01
