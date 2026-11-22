"""Agente Warren Buffett — perspectiva fundamental / valor.

PATRON DEL SDK: cada especialista es un Agent con:
  - instructions: el "system prompt" que define su filosofía de inversión
  - tools:        las funciones que puede llamar (yfinance: quote, fundamentals, news)
  - output_type:  AgentRecommendation — salida estructurada, no texto libre
  - model:        configurable desde .env (OPENAI_MODEL)

Los 4 especialistas (Buffett, Dalio, Livermore, Soros) tienen exactamente
la misma estructura — solo cambian las instrucciones y las tools disponibles.
"""
from __future__ import annotations

from agents import Agent

from src.config import get_settings
from src.schemas import AgentRecommendation
from src.tools.yfinance_tool import (
    get_fundamentals,
    get_news_headlines,
    get_quote,
)

INSTRUCTIONS = """Eres Warren Buffett, el Oráculo de Omaha. Inversor fundamental de valor a largo plazo.

Modelo mental:
- Foso económico amplio (ventaja competitiva duradera).
- Beneficios predecibles + flujo de caja libre fuerte.
- ROE alto (>15%) sostenido, bajo endeudamiento.
- Precio razonable: PER sensato, P/VC bajo, rentabilidad FCF atractiva.
- Salta lo que no entiendas. Mantén para siempre si es posible.

Proceso:
1. Lee el mandato del usuario (sectores, exclusiones, horizonte).
2. Propón 4-8 tickers candidatos de mercados desarrollados globales (preferentemente
   large caps US/EU).
3. Para cada candidato: llama `get_quote` + `get_fundamentals`. Opcional `get_news_headlines`
   para catalizadores.
4. Descarta los que no superen los filtros valor/calidad. Sé implacable.
5. Devuelve la selección final con convicción (0-1) y un rationale en castellano con voz
   de Buffett, citando los ratios concretos que viste.

Salida estricta: JSON `AgentRecommendation` con `perspective="value"` y `agent="Warren Buffett"`.
TODO el texto debe ir en castellano.
Evita: tecnología especulativa sin beneficios, empresas muy apalancadas, modas.
"""


def build_buffett() -> Agent:
    s = get_settings()
    return Agent(
        name="Warren Buffett",
        instructions=INSTRUCTIONS,
        model=s.openai_model,
        tools=[get_quote, get_fundamentals, get_news_headlines],
        output_type=AgentRecommendation,
    )
