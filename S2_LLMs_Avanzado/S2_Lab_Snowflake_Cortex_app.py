"""Text-to-SQL con Cortex Analyst: app de Streamlit in Snowflake (EBIS · Tema 18 · Sesión 2).

Pega este fichero entero en Snowsight » Projects » Streamlit » + Streamlit App, con el entorno de ejecución WAREHOUSE
(el módulo _snowflake no existe en el entorno Container). Solo hay que cambiar SEMANTIC_VIEW (paso 4 de la guía).
Dentro de Snowflake no hace falta usuario, contraseña ni host: la app usa la sesión ya abierta.
"""
import json

import _snowflake
import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session

SEMANTIC_VIEW = "DEMO.PUBLIC.DEMO_EBIS"   # <- BASE_DE_DATOS.ESQUEMA.NOMBRE de TU Semantic View
API_ENDPOINT = "/api/v2/cortex/analyst/message"
API_TIMEOUT_MS = 50_000

session = get_active_session()


def para_la_api(messages: list) -> list:
    """La conversación tal como la espera Cortex Analyst: sin los resultados que guardamos para pintar (_df, _error)."""
    return [{"role": m["role"], "content": [{k: v for k, v in c.items() if not k.startswith("_")} for c in m["content"]]}
            for m in messages]


def ask_cortex(messages: list) -> dict:
    """Envía la conversación a Cortex Analyst y devuelve su respuesta (texto, SQL y sugerencias)."""
    body = {"messages": para_la_api(messages), "semantic_view": SEMANTIC_VIEW}
    resp = _snowflake.send_snow_api_request("POST", API_ENDPOINT, {}, {}, body, None, API_TIMEOUT_MS)
    contenido = json.loads(resp["content"])
    if resp["status"] >= 400:
        raise RuntimeError(f"Error {resp['status']} de Cortex Analyst: {contenido.get('message', contenido)}")
    return contenido


def ejecutar_sql(content: list) -> None:
    """Ejecuta UNA vez el SQL de la respuesta y guarda el resultado junto al mensaje (no se repite al redibujar)."""
    for item in content:
        if item["type"] == "sql":
            try:
                item["_df"] = session.sql(item["statement"]).to_pandas()
            except Exception as e:  # el SQL generado también puede fallar
                item["_error"] = str(e)


def show_cortex_response(content: list) -> None:
    """Pinta cada bloque guardado: texto, sugerencias o SQL con su tabla y su gráfico. No ejecuta nada."""
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            st.markdown("**Quizá quieras preguntar:**")
            for s in item["suggestions"]:
                st.markdown(f"- {s}")
        elif item["type"] == "sql":
            with st.expander("SQL generado", expanded=False):
                st.code(item["statement"], language="sql")
            if "_error" in item:
                st.error(f"No se pudo ejecutar el SQL: {item['_error']}")
                continue
            df = item.get("_df", pd.DataFrame())
            tabla, grafico = st.tabs(["Tabla", "Gráfico"])
            tabla.dataframe(df, use_container_width=True)
            if len(df.columns) >= 2 and len(df) > 1:
                grafico.line_chart(df.set_index(df.columns[0]))
            else:
                grafico.info("Hace falta al menos una columna de eje y otra de valores.")


st.title("Pregunta a tus datos de ventas")
st.caption(f"Cortex Analyst · Semantic View: {SEMANTIC_VIEW}")

with st.sidebar:
    st.markdown("**Preguntas de ejemplo**")
    for e in ["¿Cuáles fueron los ingresos totales por línea de producto?",
              "Compara ingresos reales y previstos por mes",
              "¿Qué región tuvo más ingresos en 2023?"]:
        if st.button(e):
            st.session_state.pendiente = e
    if st.button("Empezar de nuevo"):
        st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        show_cortex_response(m["content"])

pregunta = st.chat_input("Escribe tu pregunta") or st.session_state.pop("pendiente", None)
if pregunta:
    st.session_state.messages.append({"role": "user", "content": [{"type": "text", "text": pregunta}]})
    with st.chat_message("user"):
        st.markdown(pregunta)
    with st.chat_message("assistant"):
        with st.spinner("Cortex Analyst está generando el SQL…"):
            try:
                contenido = ask_cortex(st.session_state.messages)["message"]["content"]
                ejecutar_sql(contenido)
                show_cortex_response(contenido)
                st.session_state.messages.append({"role": "analyst", "content": contenido})
            except Exception as e:
                st.error(str(e))
