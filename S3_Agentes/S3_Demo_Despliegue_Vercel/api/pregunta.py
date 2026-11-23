"""Función de servidor (Vercel): recibe una pregunta y responde con la API de OpenAI.

La clave vive aquí, en el servidor, como variable de entorno OPENAI_API_KEY. El navegador nunca la ve.
"""
import json
import os
from http.server import BaseHTTPRequestHandler

from openai import OpenAI

MAX_PREGUNTA = 300        # caracteres: límite sencillo para que nadie nos mande un libro
MAX_RESPUESTA = 300       # tokens de salida: tope de gasto por llamada


class handler(BaseHTTPRequestHandler):
    def _json(self, codigo, datos):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_POST(self):
        try:
            largo = int(self.headers.get("Content-Length") or 0)
            pregunta = json.loads(self.rfile.read(largo) or b"{}").get("pregunta", "").strip()
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"error": "Petición no válida."})
        if not pregunta:
            return self._json(400, {"error": "Escribe una pregunta."})
        if len(pregunta) > MAX_PREGUNTA:
            return self._json(400, {"error": f"Máximo {MAX_PREGUNTA} caracteres."})
        if not os.environ.get("OPENAI_API_KEY"):
            return self._json(500, {"error": "Falta la variable de entorno OPENAI_API_KEY en el servidor."})

        cliente = OpenAI()   # lee OPENAI_API_KEY del entorno
        r = cliente.responses.create(
            model="gpt-6-luna",
            reasoning={"effort": "low"},
            instructions="Eres el asistente de una clase de IA. Responde en español, en 3 frases como máximo.",
            input=pregunta,
            max_output_tokens=MAX_RESPUESTA,
        )
        return self._json(200, {"respuesta": r.output_text})
