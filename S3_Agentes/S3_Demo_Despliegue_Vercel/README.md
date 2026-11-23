# Demo: de localhost a internet con Vercel (sesión 3)

Una página web pública que responde preguntas con la API de OpenAI. Sirve para ver las tres piezas de cualquier app desplegada:

| Pieza | Fichero | Dónde se ejecuta |
|---|---|---|
| Página (frontend) | `index.html` | En el navegador de quien la visita |
| Función (backend) | `api/pregunta.py` | En el servidor de Vercel |
| Clave de OpenAI | variable de entorno `OPENAI_API_KEY` | Solo en el servidor: nunca en el HTML ni en el JavaScript |

## Publicarla (unos 5 minutos)

1. Sube esta carpeta a un repositorio de GitHub (o haz un fork del repo del curso).
2. Entra en [vercel.com](https://vercel.com) con tu cuenta de GitHub → **Add New… → Project** → **Import** del repositorio.
   Si la carpeta no está en la raíz del repo, en **Root Directory** elige `S3_Agentes/S3_Demo_Despliegue_Vercel`.
3. En **Environment Variables** añade `OPENAI_API_KEY` con tu clave.
4. Pulsa **Deploy**. En un minuto tienes una URL pública `https://….vercel.app`.
5. Cada `git push` vuelve a publicar la web sola; cada rama tiene su propia URL de prueba.

## Probarla en local

```bash
npm i -g vercel        # una vez
vercel dev             # http://localhost:3000, con la función /api/pregunta
```

## Antes de dejarla publicada

- La URL es pública: **cualquiera que la tenga gasta de tu clave**. Pon un límite de gasto en tu cuenta de OpenAI.
- La función ya limita la pregunta (300 caracteres) y la respuesta (300 tokens).
- Al acabar la demo, **borra o pausa el proyecto** en Vercel.
- El plan gratuito de Vercel (Hobby) es para uso personal, no comercial.
