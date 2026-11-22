"""Modelos de datos del sistema — define qué entra y qué sale de cada agente.

CONCEPTO CLAVE: output_type en OpenAI Agents SDK
  Cuando un Agent tiene output_type=MiClase, el SDK obliga al modelo a devolver
  JSON válido que encaje con esa clase Pydantic. Así pasamos datos estructurados
  entre agentes en lugar de texto libre que luego hay que parsear.

Flujo de datos:
  Mandate (entrada del usuario)
    → MacroContext       (producido por El-Erian)
    → AgentRecommendation x4  (producido por cada especialista)
    → Portfolio          (producido por el optimizador, narrado por el CIO)
"""
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class RiskProfile(str, Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class Horizon(str, Enum):
    SHORT = "short"      # < 1y
    MEDIUM = "medium"    # 1-5y
    LONG = "long"        # > 5y


class Mandate(BaseModel):
    """User input — investment brief."""
    market_situation: str = Field(..., description="Current market context narrative")
    mandate: str = Field(..., description="Investment mandate / objective")
    amount: float = Field(..., gt=0, description="Capital to allocate (EUR)")
    horizon: Horizon
    risk_profile: RiskProfile = RiskProfile.BALANCED
    base_currency: str = "EUR"
    exclusions: list[str] = Field(default_factory=list, description="Sector/ticker bans")


class TickerPick(BaseModel):
    ticker: str
    name: str | None = None
    rationale: str
    conviction: float = Field(..., ge=0, le=1, description="0-1 conviction score")
    target_weight_hint: float | None = Field(None, ge=0, le=1)


class MacroContext(BaseModel):
    """Contexto macro/mercado producido por agente con WebSearchTool."""
    regime: str = Field(..., description="Régimen económico (p.ej. 'desinflación + crecimiento moderado')")
    growth_outlook: str
    inflation_outlook: str
    monetary_policy: str = Field(..., description="Postura Fed, BCE y otros relevantes")
    market_state: str = Field(..., description="Renta variable, renta fija, materias primas")
    key_risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    narrative: str = Field(..., description="Resumen ejecutivo en castellano")
    sources: list[str] = Field(default_factory=list, description="URLs citadas")


class AgentRecommendation(BaseModel):
    """Output per specialist agent."""
    agent: str
    perspective: Literal["macro", "value", "momentum", "global"]
    thesis: str
    picks: list[TickerPick]
    avoid: list[str] = Field(default_factory=list)


class Holding(BaseModel):
    ticker: str
    name: str | None = None
    weight: float = Field(..., ge=0, le=1)
    amount_eur: float
    rationale: str


class PortfolioMetrics(BaseModel):
    expected_return: float
    volatility: float
    sharpe: float
    max_drawdown_estimate: float | None = None


class Portfolio(BaseModel):
    holdings: list[Holding]
    metrics: PortfolioMetrics
    cash_weight: float = 0.0
    narrative: str = Field(..., description="Executive summary for the user")
    contributors: list[AgentRecommendation] = Field(default_factory=list)
