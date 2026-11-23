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
   En **Framework Preset** deja **Other**: no hay nada que compilar.
3. En **Environment Variables** añade `OPENAI_API_KEY` con tu clave. Opcional: `DEMO_CODIGO` con un código; así solo responde a quien lo escriba en la página.
4. Pulsa **Deploy**. En un minuto tienes una URL pública `https://….vercel.app`.
5. Con el proyecto conectado a GitHub, cada `git push` a la rama principal publica la versión de producción, y cada rama, una versión de prueba con su propia URL.

## Probarla en local

```bash
npm i -g vercel        # una vez
vercel dev             # http://localhost:3000, con la función /api/pregunta
```

## Antes de dejarla publicada

- La URL es pública: **cualquiera que la tenga puede preguntar y gastar de tu clave**. Usa una clave de un **proyecto de OpenAI dedicado** y ponle un **límite duro de gasto** (en platform.openai.com, *Limits* del proyecto). Puede aplicarse con un pequeño retraso.
- Activa `DEMO_CODIGO` si no quieres que la use cualquiera.
- La función limita cada petición (300 caracteres de pregunta, 300 tokens de respuesta, 20 s), **no el número de peticiones**.
- Al acabar la demo, **borra o pausa el proyecto** en Vercel.
- El plan gratuito de Vercel (Hobby) es para uso personal, no comercial.
