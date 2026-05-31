# Demo: Constructor de Cartera Multiagente

App de demostración para clase — sistema multi-agente de inversión construido con **OpenAI Agents SDK**.

> No es material de ejercicios. Se usa como demo en vivo durante la Sesión 4 para mostrar
> un sistema de agentes real en producción: varios agentes en paralelo, tools con datos reales,
> salida estructurada con Pydantic y una interfaz Streamlit.

---

## Qué conceptos del SDK se ven aquí

| Concepto | Dónde aparece |
|---|---|
| `Agent` + `instructions` | Cada especialista tiene su propio system prompt con su filosofía |
| `@function_tool` | Tools de yfinance: precios, fundamentales, señales técnicas, noticias |
| `WebSearchTool` | El-Erian (macro) y Dalio/Soros usan búsqueda web en tiempo real |
| `output_type` (Pydantic) | Cada agente devuelve un objeto estructurado, no texto libre |
| `asyncio.gather` | Los 4 especialistas corren EN PARALELO — no uno tras otro |
| Agente sin tools | El CIO (Markowitz) solo razona sobre los outputs de los demás |

---

## Flujo del sistema

```
Tú introduces: mandato, importe, horizonte, perfil de riesgo, visión de mercado
        |
        v
[El-Erian]  usa WebSearch → MacroContext (régimen, riesgos, oportunidades)
        |
        v — MacroContext inyectado a todos los especialistas
        |
[Buffett]  ─┐  tools: fundamentales, noticias
[Dalio]    ─┤  tools: WebSearch, precios        →  AgentRecommendation x4 (en paralelo)
[Livermore]─┤  tools: señales técnicas, historial
[Soros]    ─┘  tools: WebSearch, noticias
        |
        v
[CIO Markowitz]  sintetiza las 4 recomendaciones → lista de tickers + narrativa
        |
        v
[Optimizador Markowitz]  PyPortfolioOpt sobre datos reales de yfinance
        |
        v
Cartera final: pesos, importes en EUR, Sharpe, retorno esperado, volatilidad
```

---

## Agentes del sistema

| Agente | Perspectiva | Tools |
|---|---|---|
| Mohamed El-Erian | Macro global (contextualiza a los demás) | WebSearchTool |
| Warren Buffett | Fundamental / Valor | `get_fundamentals`, `get_quote`, `get_news_headlines` |
| Ray Dalio | Macro / All Weather | WebSearchTool, `get_price_history` |
| Jesse Livermore | Momentum / Técnico | `get_technical_signals`, `get_price_history` |
| George Soros | Global / Reflexividad | WebSearchTool, `get_news_headlines` |
| Harry Markowitz (CIO) | Síntesis — ninguna tool, solo razonamiento | — |

---

## Estructura del código

```
src/
├── app.py            ← UI Streamlit (punto de entrada)
├── orchestrator.py   ← pipeline completo: coordina todos los agentes
├── schemas.py        ← modelos Pydantic: Mandate → MacroContext → AgentRecommendation → Portfolio
├── config.py         ← settings desde .env (modelo, pesos máximos, etc.)
├── tracing.py        ← extrae trazas del SDK para mostrarlas en la UI
├── investors/
│   ├── elerian.py    ← agente El-Erian (macro)
│   ├── buffett.py    ← agente Buffett (valor)
│   ├── dalio.py      ← agente Dalio (macro)
│   ├── livermore.py  ← agente Livermore (técnico)
│   ├── soros.py      ← agente Soros (global)
│   └── portfolio_mgr.py ← agente CIO Markowitz (síntesis)
└── tools/
    ├── yfinance_tool.py  ← @function_tool: datos de Yahoo Finance
    └── optimizer.py      ← optimización Markowitz (PyPortfolioOpt, fuera del SDK)
```

---

## Ejecutar la demo (local)

```bash
# 1. Instalar dependencias
uv venv && source .venv/bin/activate   # o .venv\Scripts\activate en Windows
uv pip install -e .

# 2. Configurar API key
cp .env.example .env
# editar .env: añadir OPENAI_API_KEY

# 3. Lanzar
streamlit run src/app.py
```

Se abre en `http://localhost:8501`.

### Configuración del modelo (`.env`)

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o              # modelo para los especialistas
OPENAI_MODEL_REASONING=o3-mini   # modelo para el CIO (síntesis)
```

---

## Docker (alternativa)

```bash
cp .env.example .env   # añadir OPENAI_API_KEY
docker compose up --build
# abrir http://localhost:8501
```

---

## Notas

- **Sin trading real.** La salida es orientativa para revisión humana.
- Yahoo Finance tiene límite de peticiones — con muchos tickers puede ser lento.
- Los agentes pueden alucinar tickers; el optimizador descarta los que no tienen historial de precios.
- El tiempo de ejecución típico es 30-90 segundos dependiendo del modelo y el número de tickers.
