"""Streamlit UI — Constructor de cartera multiagente."""
from __future__ import annotations

import locale
import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import get_settings
from src.orchestrator import run_pipeline_sync
from src.schemas import Horizon, Mandate, RiskProfile

logging.basicConfig(level=get_settings().log_level)

# Locale castellano para separadores miles (con fallback si no instalado)
for loc in ("es_ES.UTF-8", "es_ES.utf8", "es_ES", "C.UTF-8"):
    try:
        locale.setlocale(locale.LC_ALL, loc)
        break
    except locale.Error:
        continue


def fmt_eur(x: float) -> str:
    return f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_int(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".")


def fmt_pct(x: float, dec: int = 2) -> str:
    s = f"{x*100:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} %"


# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Bolsa — Cartera Multiagente",
    page_icon="📈",
    layout="wide",
)

settings = get_settings()

st.title("Constructor de Cartera Multiagente")
st.caption(
    "Pipeline: **El-Erian** (macro vía WebSearch) → **Buffett · Dalio · Livermore · Soros** "
    "(en paralelo) → **CIO Markowitz** (síntesis) → **Optimizador**. "
    f"Modelo: `{settings.openai_model}` · Modelo CIO: `{settings.openai_model_reasoning}`"
)

# --- Diagrama arquitectura -------------------------------------------------
with st.expander("Arquitectura del flujo", expanded=True):
    dot = """
    digraph G {
        rankdir=LR;
        graph [bgcolor="transparent", fontname="Helvetica"];
        node  [fontname="Helvetica", style="rounded,filled", shape=box, fontsize=11];
        edge  [fontname="Helvetica", fontsize=10, color="#666"];

        UI    [label="UI Streamlit\\n(mandato/importe/horizonte/situación)", fillcolor="#FDE68A"];
        ORQ   [label="Orquestador\\n(asyncio)", fillcolor="#A7F3D0"];

        ELE [label="Mohamed El-Erian\\nEconomista jefe", fillcolor="#FEF3C7"];
        TYE [label="OpenAI WebSearchTool\\n(external_tool)", shape=oval, fillcolor="#FCE7F3"];
        MCX [label="MacroContext\\n(régimen, riesgos, oportunidades)", fillcolor="#FEF3C7"];

        BUF [label="Warren Buffett\\nFundamental / Valor", fillcolor="#DBEAFE"];
        DAL [label="Ray Dalio\\nMacro / Top-down", fillcolor="#DBEAFE"];
        LIV [label="Jesse Livermore\\nMomentum / Técnico", fillcolor="#DBEAFE"];
        SOR [label="George Soros\\nGlobal / Reflexividad", fillcolor="#DBEAFE"];

        TY1 [label="yfinance\\nfundamentals + news", shape=oval, fillcolor="#FCE7F3"];
        TY2 [label="yfinance + WebSearch\\nmacro + precios", shape=oval, fillcolor="#FCE7F3"];
        TY3 [label="yfinance\\nseñales técnicas", shape=oval, fillcolor="#FCE7F3"];
        TY4 [label="WebSearch + news", shape=oval, fillcolor="#FCE7F3"];

        CIO [label="CIO Harry Markowitz\\nSíntesis", fillcolor="#FBCFE8"];
        OPT [label="Optimizador Markowitz\\nPyPortfolioOpt", fillcolor="#FDBA74"];
        OUT [label="Cartera óptima\\nholdings · pesos · métricas", fillcolor="#86EFAC"];

        UI -> ORQ;
        ORQ -> ELE -> TYE;
        ELE -> MCX [label="produce"];

        MCX -> BUF [style=dashed, label="contexto"];
        MCX -> DAL [style=dashed];
        MCX -> LIV [style=dashed];
        MCX -> SOR [style=dashed];
        MCX -> CIO [style=dashed];

        ORQ -> BUF -> TY1;
        ORQ -> DAL -> TY2;
        ORQ -> LIV -> TY3;
        ORQ -> SOR -> TY4;

        BUF -> CIO; DAL -> CIO; LIV -> CIO; SOR -> CIO;
        CIO -> OPT -> OUT;
    }
    """
    st.graphviz_chart(dot, use_container_width=True)

# --- Configuración actual --------------------------------------------------
with st.expander("Configuración actual del sistema", expanded=False):
    cfg_cols = st.columns(2)
    with cfg_cols[0]:
        st.markdown("**Modelos LLM**")
        st.code(
            f"Especialistas:  {settings.openai_model}\n"
            f"CIO síntesis:   {settings.openai_model_reasoning}\n"
            f"Log level:      {settings.log_level}",
            language="text",
        )
    with cfg_cols[1]:
        st.markdown("**Restricciones del optimizador**")
        st.code(
            f"Peso máx. por activo:  {fmt_pct(settings.max_weight_per_asset, 0)}\n"
            f"Mínimo de activos:     {settings.min_assets}\n"
            f"Tipo libre riesgo:     {fmt_pct(settings.risk_free_rate, 2)}",
            language="text",
        )

    st.markdown("**Agentes y herramientas**")
    agents_table = pd.DataFrame([
        {"Agente": "Mohamed El-Erian", "Perspectiva": "Economista jefe (contexto macro)",
         "Herramientas": "WebSearchTool (external_tool OpenAI)"},
        {"Agente": "Warren Buffett", "Perspectiva": "Fundamental / Valor",
         "Herramientas": "get_quote, get_fundamentals, get_news_headlines"},
        {"Agente": "Ray Dalio", "Perspectiva": "Macro / Top-down",
         "Herramientas": "WebSearchTool, get_quote, get_price_history"},
        {"Agente": "Jesse Livermore", "Perspectiva": "Momentum / Técnico",
         "Herramientas": "get_quote, get_price_history, get_technical_signals"},
        {"Agente": "George Soros", "Perspectiva": "Global / Reflexividad",
         "Herramientas": "WebSearchTool, get_quote, get_news_headlines"},
        {"Agente": "Harry Markowitz (CIO)", "Perspectiva": "Síntesis + optimización",
         "Herramientas": "—"},
    ])
    st.dataframe(agents_table, use_container_width=True, hide_index=True)

# --- Sidebar inputs --------------------------------------------------------
with st.sidebar:
    st.header("Mandato de inversión")
    amount = st.number_input(
        "Importe (€)", min_value=1_000.0, value=100_000.0, step=1_000.0, format="%.0f"
    )
    horizon_label = st.selectbox(
        "Horizonte temporal",
        options=["corto (<1 año)", "medio (1-5 años)", "largo (>5 años)"],
        index=2,
    )
    horizon = {
        "corto (<1 año)": Horizon.SHORT,
        "medio (1-5 años)": Horizon.MEDIUM,
        "largo (>5 años)": Horizon.LONG,
    }[horizon_label]
    risk_label = st.select_slider(
        "Perfil de riesgo",
        options=["conservador", "equilibrado", "agresivo"],
        value="equilibrado",
    )
    risk = {
        "conservador": RiskProfile.CONSERVATIVE,
        "equilibrado": RiskProfile.BALANCED,
        "agresivo": RiskProfile.AGGRESSIVE,
    }[risk_label]
    exclusions_raw = st.text_input(
        "Exclusiones (tickers/sectores separados por coma)", value=""
    )
    exclusions = [e.strip() for e in exclusions_raw.split(",") if e.strip()]

mandate_text = st.text_area(
    "Mandato de inversión",
    value="Construir una cartera globalmente diversificada con objetivo de revalorización del capital.",
    height=80,
)
market_text = st.text_area(
    "Situación de mercado (tu visión)",
    value=(
        "Desinflación en marcha en países desarrollados, ciclo de bajadas de la Fed "
        "comenzando, crecimiento UE débil, ciclo de capex en IA en curso, riesgo "
        "geopolítico de cola en Oriente Medio y Taiwán."
    ),
    height=100,
)

go = st.button("Construir cartera", type="primary", use_container_width=True)

# --- Ejecución -------------------------------------------------------------
if go:
    mandate = Mandate(
        market_situation=market_text,
        mandate=mandate_text,
        amount=amount,
        horizon=horizon,
        risk_profile=risk,
        exclusions=exclusions,
    )

    with st.spinner("Especialistas analizando mercados en paralelo… (1-3 min)"):
        try:
            result = run_pipeline_sync(mandate)
        except Exception as e:
            st.error(f"Fallo en el pipeline: {e}")
            st.stop()

    pf = result.portfolio

    st.success(f"Cartera generada en {result.total_duration_s:.1f} s")

    # Contexto macro (El-Erian)
    if result.macro_context:
        mc = result.macro_context
        st.subheader("Contexto macro actual (Mohamed El-Erian · WebSearch)")
        st.info(f"**Régimen:** {mc.regime}")
        mcols = st.columns(2)
        with mcols[0]:
            st.markdown(f"**Crecimiento:** {mc.growth_outlook}")
            st.markdown(f"**Inflación:** {mc.inflation_outlook}")
            st.markdown(f"**Política monetaria:** {mc.monetary_policy}")
        with mcols[1]:
            st.markdown(f"**Estado de mercados:** {mc.market_state}")
            if mc.key_risks:
                st.markdown("**Riesgos clave:**")
                for r in mc.key_risks:
                    st.markdown(f"- {r}")
            if mc.opportunities:
                st.markdown("**Oportunidades:**")
                for o in mc.opportunities:
                    st.markdown(f"- {o}")
        with st.expander("Narrativa macro completa"):
            st.markdown(mc.narrative)
            if mc.sources:
                st.markdown("**Fuentes:**")
                for url in mc.sources:
                    st.markdown(f"- {url}")

    # Métricas globales
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rentabilidad esperada (anual.)", fmt_pct(pf.metrics.expected_return))
    c2.metric("Volatilidad (anual.)", fmt_pct(pf.metrics.volatility))
    c3.metric("Ratio de Sharpe", f"{pf.metrics.sharpe:.2f}".replace(".", ","))
    c4.metric("Liquidez", fmt_pct(pf.cash_weight, 1))

    # Holdings
    st.subheader("Composición de la cartera")
    df = pd.DataFrame([h.model_dump() for h in pf.holdings])
    if not df.empty:
        df_view = pd.DataFrame({
            "Ticker": df["ticker"],
            "Peso": df["weight"].apply(lambda x: fmt_pct(x, 2)),
            "Importe (€)": df["amount_eur"].apply(fmt_eur),
            "Rationale": df["rationale"],
        })
        st.dataframe(df_view, use_container_width=True, hide_index=True)

        fig = px.pie(df, names="ticker", values="weight", title="Distribución por activo")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    # Narrativa CIO
    st.subheader("Narrativa del CIO")
    st.markdown(pf.narrative)

    # Visiones de cada especialista
    st.subheader("Visiones por especialista")
    tabs = st.tabs([r.agent for r in result.recommendations])
    for tab, rec in zip(tabs, result.recommendations):
        with tab:
            st.markdown(f"**Perspectiva:** `{rec.perspective}`")
            st.markdown(f"**Tesis:** {rec.thesis}")
            picks_df = pd.DataFrame([p.model_dump() for p in rec.picks])
            if not picks_df.empty:
                picks_df = picks_df.rename(columns={
                    "ticker": "Ticker",
                    "name": "Nombre",
                    "rationale": "Justificación",
                    "conviction": "Convicción",
                    "target_weight_hint": "Peso objetivo",
                })
                st.dataframe(picks_df, use_container_width=True, hide_index=True)
            if rec.avoid:
                st.caption(f"Evitar: {', '.join(rec.avoid)}")

    # Traza completa
    st.subheader("Traza de operaciones")
    st.caption(
        f"Universo enviado al optimizador ({len(result.optimizer_input_tickers)} tickers): "
        f"`{', '.join(result.optimizer_input_tickers)}`"
    )

    trace_tabs = st.tabs([f"{t.agent}" for t in result.traces])
    for tab, tr in zip(trace_tabs, result.traces):
        with tab:
            cT1, cT2 = st.columns([1, 1])
            cT1.metric("Llamadas a herramientas", tr.tool_call_count)
            cT2.metric("Duración", f"{(tr.duration_s or 0):.1f} s")

            if not tr.events:
                st.info("Sin eventos registrados.")
                continue

            for i, ev in enumerate(tr.events, 1):
                if ev.kind == "tool_call":
                    with st.expander(f"#{i}  🔧 tool_call → `{ev.name}`", expanded=False):
                        st.code(ev.arguments or "{}", language="json")
                elif ev.kind == "tool_output":
                    with st.expander(f"#{i}  ↩️ tool_output", expanded=False):
                        st.code(ev.output or "", language="json")
                elif ev.kind == "message":
                    with st.expander(f"#{i}  💬 message", expanded=False):
                        st.markdown(ev.text or "")
                elif ev.kind == "reasoning":
                    st.caption(f"#{i}  🧠 paso de razonamiento (oculto por el SDK)")

    with st.expander("Síntesis cruda del CIO (texto completo)"):
        st.code(result.raw_synthesis)
