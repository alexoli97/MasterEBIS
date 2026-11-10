# Máster en Data Science e IA — EBIS Business Techschool

Material práctico del **Tema 18: IA Generativa Avanzada** (edición de noviembre de 2026).

Todos los notebooks usan la **Responses API de OpenAI** con el modelo `gpt-6-luna` y razonamiento bajo (`reasoning={"effort": "low"}`), y se pueden abrir directamente en Google Colab.

---

## Antes de empezar

1. Lee la [guía previa](00_Preparacion/Guia_previa_Tema18.pdf).
2. Configura tu API key de OpenAI como **secreto de Colab** llamado `OPENAI_API_KEY` (icono de la llave en la barra izquierda) o como variable de entorno en tu ordenador. **Nunca la escribas dentro de un notebook.**
3. Ejecuta [`00_Preparacion/00_Preparacion_entorno.ipynb`](00_Preparacion/00_Preparacion_entorno.ipynb). Si al final ves «✅ Todo listo», ya estás.

Para abrir cualquier notebook en Colab: `https://colab.research.google.com/github/alexoli97/MasterEBIS/blob/main/<ruta del notebook>`.

**Convención de nombres:** `X_Alumnos.ipynb` es la versión con huecos (`TODO`) y `X.ipynb` la resuelta. Los labs `_EnClase` se hacen en directo durante la sesión.

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
| `Lab_LLM_EnClase_1.ipynb` | En clase: Responses API, tokens y coste, parámetros de un modelo que razona, prompting |
| `Mini_RAG_Demo.ipynb` | Demo en clase: mini-RAG sobre una empresa ficticia con respuestas citadas |
| `Lab_LLM_API_Basico_Alumnos.ipynb` · `Lab_LLM_API_Basico.ipynb` | Reto: anatomía de la respuesta, razonamiento, streaming, salida estructurada con Pydantic, fallos típicos y evaluación |
| `Lab_NLP.ipynb` · `Lab_NLP_Solución.ipynb` | Reto opcional: de Bag of Words y Word2Vec a un mini GPT con atención |
| `Lab_RAG_Avanzado_Alumnos.ipynb` · `Lab_RAG_Avanzado.ipynb` | Reto: chunking, ChromaDB, búsqueda híbrida con RRF, re-ranking, citas y evaluación |

## Sesión 2 — Multimodal y producción (`S2_LLMs_Avanzado/`)

| Notebook | Qué es |
|---|---|
| `Lab_LLM_EnClase_2.ipynb` | En clase: visión (fotos y gráficos), generación de imágenes, coste por modelo y prompt caching |
| `Lab_Evals_EnClase.ipynb` | En clase: dataset de evaluación, reglas en código, juez con rúbrica y comparación de variantes |
| `Lab_Decisions_EnClase.ipynb` | En clase: decision models frente a generativo en un triaje de tickets |
| `Lab_Streamlit_EnClase.ipynb` | En clase: una app de Streamlit en directo |
| `Lab_Snowflake_Cortex_EnClase.ipynb` | Guía en clase: Text-to-SQL con Snowflake Cortex Analyst (datos en `cortex_data/`) |
| `Lab_Agente_SQL_Alumnos.ipynb` · `Lab_Agente_SQL.ipynb` | Reto: agente analista de datos sin framework, con tools, guardarraíles, evaluación y chatbot en Streamlit |

## Sesión 3 — Agentes y vibe coding (`S3_Agentes/`)

| Material | Qué es |
|---|---|
| `Lab_MCP.ipynb` | En clase: servidor MCP propio, MCP Inspector y conexión con un LLM |
| `Lab_Copilot_Studio.pdf` · `Bicis_Nube_Manual_interno.pdf` | En clase: construcción de un agente de soporte en Copilot Studio con el manual de una empresa ficticia |
| `Reto_S3_VibeCoding.ipynb` | Retos opcionales de vibe coding: asistente RAG o dashboard en Streamlit |

## Sesión 4 — Prototipado de agentes (`S4_Agentes_Avanzado/`)

| Material | Qué es |
|---|---|
| `LangChain_LangGraph/Lab_LangChain_LangGraph_EnClase.ipynb` | En clase: LangChain 1.x (`create_agent`, middleware) y LangGraph |
| `LangChain_LangGraph/Ejercicio_LangGraph_Alumnos.ipynb` · `_Resuelto.ipynb` | Workshop: agente de soporte IT con estado, ramas y aprobación humana |
| `OpenAI_Agents/1_Agents.ipynb` | Workshop: OpenAI Agents SDK con el caso TravelMind (tools, salida tipada, handoffs, guardrails, sessions, MCP) |
| `OpenAI_Agents/2_Reto_asistente.ipynb` · `_SOLUCION.ipynb` | Reto final: asistente de viajes con RAG sobre PDFs, citas, guardarraíles y eval set (`data/manuals/`, `tests/cases.yaml`) |
| `OpenAI_Agents/Demo_Bolsa_Multiagente/` | Demo: sistema multi-agente de análisis bursátil con Streamlit (ver su README) |

---

## Recursos para seguir aprendiendo

- Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- OpenAI, [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- Simon Willison, [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- [Model Context Protocol](https://modelcontextprotocol.io) · [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) · [LangGraph](https://docs.langchain.com/oss/python/langgraph)
