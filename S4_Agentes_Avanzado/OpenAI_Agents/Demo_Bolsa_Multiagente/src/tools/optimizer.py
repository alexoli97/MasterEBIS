"""Optimizador de cartera Markowitz — función pura, no es un agente.

NOTA ARQUITECTURAL: este módulo NO usa el SDK de agentes.
  Es código Python clásico que corre FUERA del loop de agentes.
  El orquestador lo llama directamente tras recibir la lista de tickers del CIO.

  Esto ilustra un patrón común: los agentes razonan y seleccionan,
  pero el cálculo determinista (optimización matemática) lo hace código normal.

Qué hace:
  1. Descarga 3 años de precios históricos con yfinance
  2. Calcula retornos esperados y matriz de covarianza (Ledoit-Wolf shrinkage)
  3. Optimiza según el perfil de riesgo:
     - conservador → mínima volatilidad
     - equilibrado/agresivo → máximo Sharpe
  4. Aplica restricción de peso máximo por activo (configurable en .env)
  5. Devuelve Portfolio con holdings, pesos, importes en EUR y métricas
"""
from __future__ import annotations

import pandas as pd
from pypfopt import EfficientFrontier, expected_returns, risk_models

from src.config import get_settings
from src.schemas import Holding, Mandate, Portfolio, PortfolioMetrics, RiskProfile
from src.tools.yfinance_tool import fetch_prices


def _objective_for_profile(profile: RiskProfile) -> str:
    return {
        RiskProfile.CONSERVATIVE: "min_volatility",
        RiskProfile.BALANCED: "max_sharpe",
        RiskProfile.AGGRESSIVE: "max_sharpe",
    }[profile]


def optimize(
    tickers: list[str],
    mandate: Mandate,
    rationale_by_ticker: dict[str, str] | None = None,
) -> Portfolio:
    """Run Markowitz optimization with mandate constraints.

    Returns Portfolio with metrics + holdings.
    """
    s = get_settings()
    rationale_by_ticker = rationale_by_ticker or {}

    # dedup + clean
    tickers = sorted({t.strip().upper() for t in tickers if t and t.strip()})
    if len(tickers) < 2:
        raise ValueError("Need >=2 tickers to optimize")

    prices = fetch_prices(tickers, period="3y")
    if prices.shape[1] < 2:
        raise ValueError(f"Insufficient price data for tickers: {tickers}")

    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()

    max_w = s.max_weight_per_asset
    if mandate.risk_profile == RiskProfile.AGGRESSIVE:
        max_w = min(0.35, max_w * 1.5)
    elif mandate.risk_profile == RiskProfile.CONSERVATIVE:
        max_w = min(max_w, 0.15)

    ef = EfficientFrontier(mu, S, weight_bounds=(0, max_w))
    obj = _objective_for_profile(mandate.risk_profile)
    if obj == "min_volatility":
        ef.min_volatility()
    else:
        ef.max_sharpe(risk_free_rate=s.risk_free_rate)

    weights = ef.clean_weights()
    expected_ret, vol, sharpe = ef.portfolio_performance(risk_free_rate=s.risk_free_rate)

    holdings: list[Holding] = []
    for tk, w in weights.items():
        if w <= 0.005:  # drop dust
            continue
        holdings.append(Holding(
            ticker=tk,
            weight=float(w),
            amount_eur=round(float(w) * mandate.amount, 2),
            rationale=rationale_by_ticker.get(tk, "Optimizer allocation"),
        ))

    holdings.sort(key=lambda h: h.weight, reverse=True)
    cash = max(0.0, 1.0 - sum(h.weight for h in holdings))

    metrics = PortfolioMetrics(
        expected_return=float(expected_ret),
        volatility=float(vol),
        sharpe=float(sharpe),
    )

    return Portfolio(
        holdings=holdings,
        metrics=metrics,
        cash_weight=cash,
        narrative="",  # filled by portfolio_mgr agent
    )
