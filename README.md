# Máster en Data Science e IA — EBIS Business Techschool

Material práctico del **Tema 18: IA Generativa Avanzada** (edición de noviembre de 2026).

Todos los notebooks usan la **Responses API de OpenAI** con el modelo `gpt-6-luna` y razonamiento bajo (`reasoning={"effort": "low"}`), y se pueden abrir directamente en Google Colab.

---

## Antes de empezar

1. Lee la [guía previa](00_Preparacion/S0_Guia_Previa.pdf).
2. Configura tu API key de OpenAI como **secreto de Colab** llamado `OPENAI_API_KEY` (icono de la llave en la barra izquierda) o como variable de entorno en tu ordenador. **Nunca la escribas dentro de un notebook.**
3. Ejecuta [`00_Preparacion/S0_Preparacion_Entorno.ipynb`](00_Preparacion/S0_Preparacion_Entorno.ipynb). Si al final ves «✅ Todo listo», ya estás.

Para abrir cualquier notebook en Colab: `https://colab.research.google.com/github/alexoli97/MasterEBIS/blob/main/<ruta del notebook>`.

**Convención de nombres:** `S{sesión}_{tipo}_{tema}`. **Lab** = se hace en clase · **Reto** = entre sesiones · **Demo** = la enseña el profesor. La versión con huecos (`TODO`) no lleva sufijo; la resuelta termina en `_Solucion`.

---

## Estructura

```
MasterEBIS/
├── 00_Preparacion/        Guía previa y notebook de comprobación del entorno
├── S1_LLMs/               Sesión 1 · LLMs, uso por API, razonamiento y RAG
├── S2_LLMs_Avanzado/      Sesión 2 · Multimodal, producción (evals, decision models) y Data Science
├── S3_Agentes/            Sesión 3 · MCP, Copilot Studio y vibe coding
└── S4_Agentes_Avanzado/   Sesión 4 · LangChain / LangGraph, OpenAI Agents SDK y reto final
```

---

## Sesión 1 — LLMs (`S1_LLMs/`)

| Notebook | Qué es |
|---|---|
| `S1_Lab_LLM_API.ipynb` | En clase: Responses API, tokens y coste, parámetros de un modelo que razona, prompting |
| `S1_Demo_MiniRAG.ipynb` | Demo en clase: mini-RAG sobre una empresa ficticia con respuestas citadas |
| `S1_Reto_LLM_API.ipynb` · `_Solucion` | Reto: anatomía de la respuesta, razonamiento, streaming, salida estructurada con Pydantic, fallos típicos y evaluación |
| `S1_Reto_NLP.ipynb` · `_Solucion` | Reto opcional: de Bag of Words y Word2Vec a un mini GPT con atención |
| `S1_Reto_RAG_Avanzado.ipynb` · `_Solucion` | Reto: chunking, ChromaDB, búsqueda híbrida con RRF, re-ranking, citas y evaluación |

## Sesión 2 — Multimodal y producción (`S2_LLMs_Avanzado/`)

| Notebook | Qué es |
|---|---|
| `S2_Lab_Multimodal_Produccion.ipynb` | En clase: visión (fotos y gráficos), generación de imágenes, coste por modelo y prompt caching |
| `S2_Lab_Evals.ipynb` | En clase: dataset de evaluación, reglas en código, juez con rúbrica y comparación de variantes |
| `S2_Lab_Decisions.ipynb` | En clase: decision models frente a generativo en un triaje de tickets |
| `S2_Lab_Streamlit.ipynb` | En clase: una app de Streamlit en directo |
| `S2_Lab_Snowflake_Cortex.ipynb` · `S2_Lab_Snowflake_Cortex_app.py` | Guía en clase: Text-to-SQL con Snowflake Cortex Analyst (datos en `cortex_data/`) y la app de Streamlit in Snowflake completa |
| `S2_Reto_Agente_SQL.ipynb` · `_Solucion` | Reto: agente analista de datos sin framework, con tools, guardarraíles, evaluación y chatbot en Streamlit |

## Sesión 3 — Agentes y vibe coding (`S3_Agentes/`)

| Material | Qué es |
|---|---|
| `S3_Lab_MCP.ipynb` | En clase: servidor MCP propio, MCP Inspector y conexión con un LLM |
| `S3_Lab_Copilot_Studio.pdf` · `S3_Bicis_Nube_Manual.pdf` | En clase: construcción de un agente de soporte en Copilot Studio con el manual de una empresa ficticia |
| `S3_Reto_VibeCoding.ipynb` | Reto opcional de vibe coding en tres niveles: dashboard en Streamlit, agente con API o servidor MCP propio |

## Sesión 4 — Prototipado de agentes (`S4_Agentes_Avanzado/`)

| Material | Qué es |
|---|---|
| `LangChain_LangGraph/S4_Lab_LangChain_LangGraph.ipynb` | En clase: LangChain 1.x (`create_agent`, middleware) y LangGraph |
| `LangChain_LangGraph/S4_Lab_LangGraph_SoporteIT.ipynb` · `_Solucion` | En clase, guiado: agente de soporte IT con estado, ramas y aprobación humana opcional |
| `OpenAI_Agents/S4_Lab_Agents_SDK.ipynb` | Workshop: OpenAI Agents SDK con el caso TravelMind (tools, salida tipada, handoffs, guardrails, sessions, MCP) |
| `OpenAI_Agents/S4_Reto_Asistente_Viajes.ipynb` · `_Solucion` | Reto final: asistente de viajes con RAG sobre PDFs, citas, guardarraíles y eval set (`data/manuals/`, `tests/cases.yaml`) |
| `OpenAI_Agents/S4_Demo_Bolsa_Multiagente/` | Demo: sistema multi-agente de análisis bursátil con Streamlit (ver su README) |

---

## Recursos para seguir aprendiendo

- Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- OpenAI, [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- Simon Willison, [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- [Model Context Protocol](https://modelcontextprotocol.io) · [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) · [LangGraph](https://docs.langchain.com/oss/python/langgraph)
