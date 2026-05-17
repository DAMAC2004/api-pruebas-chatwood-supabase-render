from fastapi import FastAPI
from routers import supabase_router, telegram_router, chatwoot_router

app = FastAPI(
    title="API Pruebas - Telegram + Chatwoot",
    description="Bot de Telegram con escalado a agente humano via Chatwoot",
    version="1.0.0",
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(supabase_router.router)
app.include_router(telegram_router.router)
app.include_router(chatwoot_router.router)


# ── Healthcheck ───────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Endpoint raíz para verificar que la API está corriendo."""
    return {"status": "ok", "message": "API Pruebas corriendo ✅"}
