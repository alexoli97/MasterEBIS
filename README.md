# Master IA & Data Science — EBIS Business School

Material de laboratorio del **Bloque B: Modelos de Lenguaje y Agentes IA**.

---

## Estructura del repositorio

```
MasterEBIS/
├── S1_LLMs/               # Sesión 1 — LLMs, NLP y RAG
├── S2_LLMs_Avanzado/      # Sesión 2 — LLMs avanzados, visión, Streamlit, Snowflake
├── S3_Agentes/            # Sesión 3 — Agentes con n8n (sin notebooks)
└── S4_Agentes_Avanzado/   # Sesión 4 — Agentes con código: LangGraph y OpenAI Agents SDK
```

---

## Sesión 1 — LLMs, NLP y RAG (`S1_LLMs/`)

Introducción a los modelos de lenguaje, procesamiento de texto y recuperación aumentada con generación.

| Notebook | Descripción |
|---|---|
| `Lab_LLM_EnClase_1.ipynb` | Lab en clase: primeros pasos con la API de OpenAI |
| `Lab_LLM_API_Basico.ipynb` | Solución: uso básico de la API (completions, chat, embeddings) |
| `Lab_LLM_API_Basico_Alumnos.ipynb` | Versión alumnos con TODOs |
| `Lab_NLP.ipynb` | Solución: preprocesamiento de texto, tokenización, similitud semántica |
| `Lab_NLP_Solución.ipynb` | Solución completa del lab NLP |
| `Lab_RAG_Avanzado.ipynb` | Solución: RAG con vectorstore, reranking y evaluación |
| `Lab_RAG_Avanzado_Alumnos.ipynb` | Versión alumnos con TODOs |
| `Mini_RAG_Demo.ipynb` | Demo rápida de RAG básico para clase |

---

## Sesión 2 — LLMs Avanzados (`S2_LLMs_Avanzado/`)

Modelos de visión (CNN, GANs, RNN), interfaces con Streamlit, Text-to-SQL y Snowflake Cortex.

| Notebook | Descripción |
|---|---|
| `Lab_LLM_EnClase_2.ipynb` | Lab en clase: técnicas avanzadas de prompting y fine-tuning |
| `Lab_CNN_Solución.ipynb` | Redes convolucionales para clasificación de imágenes |
| `Lab_GANs_Solución.ipynb` | Generative Adversarial Networks |
| `Lab_RNN_Generación_Texto_Solución.ipynb` | RNN para generación de texto (datos en `Data_Lab_RNN/`) |
| `Lab_TextToSQL_Vanna.ipynb` | Solución: consultas en lenguaje natural sobre una BD con Vanna |
| `Lab_TextToSQL_Vanna_Alumnos.ipynb` | Versión alumnos con TODOs |
| `Lab_Streamlit.ipynb` | Solución: construcción de apps de IA con Streamlit |
| `Lab_Streamlit_Alumnos.ipynb` | Versión alumnos con TODOs |
| `Lab_Streamlit_EnClase.ipynb` | Lab en clase: live coding de una app Streamlit |
| `Lab_Snowflake_Cortex_EnClase.ipynb` | Lab en clase: Snowflake Cortex — LLM nativo en el data warehouse |

**Datos**: `cortex_data/` contiene los CSVs de ventas usados en el lab de Snowflake Cortex.

---

## Sesión 3 — Agentes con n8n (`S3_Agentes/`)

Construcción de agentes sin código con **n8n** (flujos visuales, herramientas, memoria).  
No hay notebooks — el material es la instancia de n8n del curso.

---

## Sesión 4 — Agentes Avanzados con código (`S4_Agentes_Avanzado/`)

Dos frameworks para construir agentes con código: **LangChain/LangGraph** y **OpenAI Agents SDK**.

### LangChain & LangGraph

| Archivo | Para quién | Contenido |
|---|---|---|
| `Lab_LangChain_LangGraph_EnClase.ipynb` | Clase | LCEL, Pydantic, agente ReAct con tools, LangGraph con estado, HITL, LangSmith |
| `Ejercicio_LangGraph_Alumnos.ipynb` | Alumnos | Ejercicio 1 (Soporte IT) + Ejercicio 2 (Text-to-SQL) con TODOs |
| `Ejercicio_LangGraph_Resuelto.ipynb` | Profesor | Solución completa + bonus HITL |
| `img/` | Notebooks | Diagramas: LCEL pipe, grafo con estado, ReAct loop, HITL |

### OpenAI Agents SDK (`Lab_OpenAI_Agents/`)

| Archivo | Para quién | Contenido |
|---|---|---|
| `1_Agents.ipynb` | Clase | SDK completo: Agent, tools, async, salida estructurada, handoffs, guardrails, sessions + ejemplo integrador multi-agente de viajes |
| `2_Reto_asistente.ipynb` | Alumnos | Reto: construir un asistente RAG sobre guías de viaje en PDF con TODOs |
| `2_Reto_asistente_SOLUCION.ipynb` | Profesor | Solución completa del reto |
| `data/manuals/` | Reto | PDFs de guías de viaje (Japón, Portugal, Tailandia) |
| `tests/cases.yaml` | Reto | 5 preguntas de evaluación del RAG |

---

## Requisitos generales

Cada notebook incluye su celda de instalación de dependencias. En general:

```bash
# Sesiones 1-2
pip install openai langchain chromadb pandas streamlit vanna

# Sesión 4 — LangGraph
pip install langchain langgraph langchain-openai

# Sesión 4 — OpenAI Agents SDK
uv pip install openai-agents nest_asyncio chromadb pypdf pyyaml
```

Se necesita una `OPENAI_API_KEY` válida en todas las sesiones.
