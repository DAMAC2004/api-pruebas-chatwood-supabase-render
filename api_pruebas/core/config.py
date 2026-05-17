import os
from supabase import create_client, Client

# Las variables de entorno se configuran directamente en Render.
# No se usa .env en producción.

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL: str = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ── Chatwoot ──────────────────────────────────────────────────────────────────
CHATWOOT_BASE_URL: str  = os.getenv("CHATWOOT_BASE_URL", "https://app.chatwoot.com")
CHATWOOT_API_TOKEN: str = os.getenv("CHATWOOT_API_TOKEN", "")
CHATWOOT_ACCOUNT_ID: str = os.getenv("CHATWOOT_ACCOUNT_ID", "")
CHATWOOT_INBOX_ID: str  = os.getenv("CHATWOOT_INBOX_ID", "")
