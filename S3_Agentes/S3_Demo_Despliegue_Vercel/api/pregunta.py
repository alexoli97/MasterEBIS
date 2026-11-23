"""Función de servidor (Vercel): recibe una pregunta y responde con la API de OpenAI.

La clave vive aquí, en el servidor, como variable de entorno OPENAI_API_KEY. El navegador nunca la ve.
Opcional: si defines la variable DEMO_CODIGO, solo responde a quien escriba ese código en la página.
"""
import json
import os
from http.server import BaseHTTPRequestHandler

import openai
from openai import OpenAI

MAX_CUERPO = 2_000        # bytes: no leemos peticiones más grandes
MAX_PREGUNTA = 300        # caracteres
MAX_RESPUESTA = 300       # tokens de salida: tope de gasto por llamada (sin razonamiento, todo es texto visible)


class handler(BaseHTTPRequestHandler):
    def _json(self, codigo, datos):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_POST(self):
        # 1) validar la petición antes de gastar nada
        try:
            largo = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._json(400, {"error": "Petición no válida."})
        if largo > MAX_CUERPO:
            return self._json(413, {"error": "Petición demasiado grande."})
        try:
            datos = json.loads(self.rfile.read(largo) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._json(400, {"error": "Petición no válida."})
        if not isinstance(datos, dict) or not isinstance(datos.get("pregunta", ""), str):
            return self._json(400, {"error": "Petición no válida."})
        pregunta = datos.get("pregunta", "").strip()
        if not pregunta:
            return self._json(400, {"error": "Escribe una pregunta."})
        if len(pregunta) > MAX_PREGUNTA:
            return self._json(400, {"error": f"Máximo {MAX_PREGUNTA} caracteres."})
        codigo = os.environ.get("DEMO_CODIGO")
        if codigo and datos.get("codigo") != codigo:
            return self._json(403, {"error": "Código de acceso incorrecto."})
        if not os.environ.get("OPENAI_API_KEY"):
            return self._json(500, {"error": "Falta la variable de entorno OPENAI_API_KEY en el servidor."})

        # 2) llamar al modelo, con tiempo máximo y errores que la página entiende
        try:
            cliente = OpenAI(timeout=20, max_retries=1)   # lee OPENAI_API_KEY del entorno
            r = cliente.responses.create(
                model="gpt-6-luna",
                reasoning={"effort": "none"},              # sin razonamiento: los 300 tokens son de respuesta
                instructions="Eres el asistente de una clase de IA. Responde en español, en 3 frases como máximo.",
                input=pregunta,
                max_output_tokens=MAX_RESPUESTA,
            )
        except openai.AuthenticationError:
            return self._json(502, {"error": "La clave de OpenAI del servidor no es válida."})
        except openai.RateLimitError:
            return self._json(429, {"error": "Se ha agotado la cuota o hay demasiadas peticiones. Prueba más tarde."})
        except openai.APITimeoutError:
            return self._json(504, {"error": "El modelo ha tardado demasiado. Prueba otra vez."})
        except openai.APIError:
            return self._json(502, {"error": "El servicio de IA ha dado un error. Prueba otra vez."})

        texto = r.output_text.strip()
        if r.status == "incomplete" and not texto:
            return self._json(502, {"error": "La respuesta se ha cortado. Prueba con una pregunta más concreta."})
        return self._json(200, {"respuesta": texto})
