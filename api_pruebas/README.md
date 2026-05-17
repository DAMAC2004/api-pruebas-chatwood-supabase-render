# API Pruebas — Telegram Bot + Chatwoot

API construida con **FastAPI** y desplegada en **Render**.

## Estructura del proyecto

```
api_pruebas/
├── main.py                        # Punto de entrada de FastAPI
├── requirements.txt               # Dependencias
├── .env.example                   # Variables de entorno de ejemplo
├── core/
│   └── config.py                  # Configuración y clientes (Supabase, Telegram, Chatwoot)
├── models/
│   └── schemas.py                 # Modelos Pydantic (validación de datos)
├── services/
│   ├── supabase_service.py        # Lógica de base de datos
│   ├── telegram_service.py        # Envío de mensajes a Telegram
│   └── chatwoot_service.py        # Crear contactos/conversaciones en Chatwoot
└── routers/
    ├── supabase_router.py         # Endpoints del grupo Supabase
    ├── telegram_router.py         # Webhook de Telegram
    └── chatwoot_router.py         # Webhook de Chatwoot
```

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Healthcheck |
| GET | `/prueba/supabase/verificar-registro?chat_id=...` | Verifica si existe registro |
| POST | `/prueba/supabase/generar-registro` | Crea registro en ambas tablas |
| POST | `/prueba/supabase/generar-registro-mensaje` | Agrega un mensaje a registro existente |
| PATCH | `/prueba/supabase/actualizar-registro` | Cambia modo a "humano" |
| POST | `/webhook/telegram` | Webhook principal de Telegram |
| POST | `/chatwoot-webhook` | Webhook de respuestas del agente en Chatwoot |

## Configuración local

1. Clonar el repositorio
2. Crear `.env` basado en `.env.example` y completar los valores
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Correr la API:
   ```bash
   uvicorn main:app --reload
   ```
5. Abrir la documentación interactiva: http://localhost:8000/docs

## Despliegue en Render

1. Crear un nuevo **Web Service** en Render
2. Conectar el repositorio de GitHub
3. Configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Agregar las variables de entorno en el panel de Render (ver `.env.example`)

## Registrar el webhook de Telegram

Una vez desplegado en Render, registrar el webhook apuntando a la ruta correcta:

```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://api-pruebas-i14m.onrender.com/webhook/telegram
```

Verificar con:
```
https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

## Configurar el webhook de Chatwoot

En Chatwoot → Settings → Inboxes → tu inbox API → Configuration:
- **Callback URL:** `https://api-pruebas-i14m.onrender.com/chatwoot-webhook`
