import httpx
from core.config import TELEGRAM_API_URL


async def enviar_mensaje(chat_id: int | str, texto: str) -> dict:
    """
    Envía un mensaje de texto al usuario en Telegram.
    Usa la API sendMessage de Telegram Bot API.
    """
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "HTML",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
