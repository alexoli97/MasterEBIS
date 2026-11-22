"""Orquestador multiagente — punto de entrada del pipeline completo.

CONCEPTOS DEL SDK QUE SE USAN AQUI:
  - Runner.run()       → ejecuta un agente de forma asíncrona
  - asyncio.gather()   → lanza los 4 especialistas EN PARALELO (no uno a uno)
  - output_type        → cada agente devuelve un objeto Pydantic, no texto libre

FLUJO:
  1. El-Erian  (WebSearchTool)          → MacroContext  (contexto macro en vivo)
  2. Buffett · Dalio · Livermore · Soros (en paralelo, con MacroContext inyectado)
                                        → AgentRecommendation x4
  3. CIO Markowitz                      → síntesis narrativa + lista de tickers
  4. Optimizador Markowitz (PyPortfolioOpt) → pesos finales + métricas

La función pública es run_pipeline_sync(mandate) — la llama Streamlit.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field

from agents import Agent, Runner

from src.investors.buffett import build_buffett
from src.investors.dalio import build_dalio
from src.investors.elerian import build_elerian
from src.investors.livermore import build_livermore
from src.investors.portfolio_mgr import build_portfolio_mgr
from src.investors.soros import build_soros
from src.schemas import AgentRecommendation, MacroContext, Mandate, Portfolio
from src.tools.optimizer import optimize
from src.tracing import AgentTrace, extract_trace

log = logging.getLogger(__name__)


@dataclass
class RunResult:
    portfolio: Portfolio
    recommendations: list[AgentRecommendation]
    raw_synthesis: str
    macro_context: MacroContext | None = None
    traces: list[AgentTrace] = field(default_factory=list)
    total_duration_s: float = 0.0
    optimizer_input_tickers: list[str] = field(default_factory=list)


def _mandate_block(m: Mandate) -> str:
    return (
        f"## Mandato de inversión\n"
        f"- Importe: {m.amount:,.0f} {m.base_currency}\n"
        f"- Horizonte: {m.horizon.value}\n"
        f"- Perfil de riesgo: {m.risk_profile.value}\n"
        f"- Mandato: {m.mandate}\n"
        f"- Situación de mercado (visión del usuario): {m.market_situation}\n"
        f"- Exclusiones: {', '.join(m.exclusions) if m.exclusions else 'ninguna'}\n"
    )


def _macro_block(ctx: MacroContext | None) -> str:
    if ctx is None:
        return ""
    return (
        "## Contexto macro actual (Mohamed El-Erian, basado en WebSearch en vivo)\n"
        f"- Régimen: {ctx.regime}\n"
        f"- Crecimiento: {ctx.growth_outlook}\n"
        f"- Inflación: {ctx.inflation_outlook}\n"
        f"- Política monetaria: {ctx.monetary_policy}\n"
        f"- Estado de mercados: {ctx.market_state}\n"
        f"- Riesgos clave: {'; '.join(ctx.key_risks) if ctx.key_risks else '—'}\n"
        f"- Oportunidades: {'; '.join(ctx.opportunities) if ctx.opportunities else '—'}\n"
        f"\n{ctx.narrative}\n"
    )


def _specialist_prompt(mandate: Mandate, macro: MacroContext | None) -> str:
    return (
        _macro_block(macro)
        + "\n"
        + _mandate_block(mandate)
        + "\nUsa el contexto macro anterior para fundamentar tu recomendación. "
        "Produce ahora tu recomendación de especialista."
    )


async def _run_specialist(
    agent: Agent, prompt: str
) -> tuple[AgentRecommendation | None, AgentTrace]:
    t0 = time.perf_counter()
    try:
        result = await Runner.run(agent, input=prompt, max_turns=20)
        dur = time.perf_counter() - t0
        trace = extract_trace(agent.name, result, duration_s=dur)
        out = result.final_output
        if isinstance(out, AgentRecommendation):
            return out, trace
        log.warning("Agente %s devolvió salida no estructurada", agent.name)
        return None, trace
    except Exception as e:
        log.exception("Agente %s falló: %s", agent.name, e)
        trace = AgentTrace(agent=agent.name, duration_s=time.perf_counter() - t0)
        return None, trace


async def _run_macro(mandate: Mandate) -> tuple[MacroContext | None, AgentTrace]:
    t0 = time.perf_counter()
    elerian = build_elerian()
    prompt = (
        _mandate_block(mandate)
        + "\nGenera el `MacroContext` global ahora, usando WebSearchTool. "
        "Cita las URLs en `sources`."
    )
    try:
        result = await Runner.run(elerian, input=prompt, max_turns=15)
        trace = extract_trace(elerian.name, result, duration_s=time.perf_counter() - t0)
        out = result.final_output
        if isinstance(out, MacroContext):
            return out, trace
        log.warning("El-Erian devolvió salida no estructurada")
        return None, trace
    except Exception as e:
        log.exception("El-Erian falló: %s", e)
        return None, AgentTrace(agent=elerian.name, duration_s=time.perf_counter() - t0)


async def run_pipeline(mandate: Mandate) -> RunResult:
    t_start = time.perf_counter()
    traces: list[AgentTrace] = []

    # 1) Macro contexto
    macro, macro_trace = await _run_macro(mandate)
    traces.append(macro_trace)

    # 2) Especialistas en paralelo, con macro inyectado
    prompt = _specialist_prompt(mandate, macro)
    specialists = [build_buffett(), build_dalio(), build_livermore(), build_soros()]
    results = await asyncio.gather(*(_run_specialist(a, prompt) for a in specialists))

    recs: list[AgentRecommendation] = []
    for rec, tr in results:
        traces.append(tr)
        if rec is not None:
            recs.append(rec)

    if not recs:
        raise RuntimeError("Ningún especialista produjo recomendación válida")

    # 3) Síntesis CIO
    cio = build_portfolio_mgr()
    synth_prompt = (
        _macro_block(macro)
        + "\n"
        + _mandate_block(mandate)
        + "\n## Recomendaciones de los especialistas\n"
        + "\n\n".join(r.model_dump_json(indent=2) for r in recs)
        + "\n\nDevuelve la lista consolidada de tickers (uno por línea, en mayúsculas, "
        "formato Yahoo) seguido de una sección '## Narrativa' con el resumen ejecutivo en castellano."
    )
    t_cio = time.perf_counter()
    cio_result = await Runner.run(cio, input=synth_prompt, max_turns=8)
    traces.append(extract_trace(cio.name, cio_result, duration_s=time.perf_counter() - t_cio))
    synthesis_text: str = cio_result.final_output  # type: ignore[assignment]

    tickers, narrative = _parse_synthesis(synthesis_text)
    if len(tickers) < 2:
        tickers = sorted({p.ticker.upper() for r in recs for p in r.picks})

    rationale_by_ticker = {
        p.ticker.upper(): f"[{r.agent}] {p.rationale}"
        for r in recs for p in r.picks
    }

    # 4) Optimizador
    portfolio = optimize(tickers, mandate, rationale_by_ticker=rationale_by_ticker)
    portfolio.narrative = narrative or synthesis_text
    portfolio.contributors = recs

    return RunResult(
        portfolio=portfolio,
        recommendations=recs,
        raw_synthesis=synthesis_text,
        macro_context=macro,
        traces=traces,
        total_duration_s=time.perf_counter() - t_start,
        optimizer_input_tickers=tickers,
    )


def _parse_synthesis(text: str) -> tuple[list[str], str]:
    """Separa lista de tickers + narrativa del CIO."""
    marker_es = "## Narrativa"
    marker_en = "## Narrative"
    if marker_es in text:
        head, narrative = text.split(marker_es, 1)
    elif marker_en in text:
        head, narrative = text.split(marker_en, 1)
    else:
        head, narrative = text, ""
    narrative = narrative.strip()

    tickers: list[str] = []
    for line in head.splitlines():
        s = line.strip().lstrip("-*0123456789. ").strip()
        if not s or " " in s:
            continue
        if 1 <= len(s) <= 12 and s.replace(".", "").replace("-", "").isalnum():
            tickers.append(s.upper())
    return list(dict.fromkeys(tickers)), narrative


def run_pipeline_sync(mandate: Mandate) -> RunResult:
    return asyncio.run(run_pipeline(mandate))
