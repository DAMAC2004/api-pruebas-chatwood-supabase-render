import httpx
from core.config import TELEGRAM_API_URL
import services.supabase_service as db
import services.chatwoot_service as cw


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
        result = response.json()

    # Intentar reflejar la respuesta del BOT en Chatwoot (si existe conversación)
    try:
        registro = db.obtener_registro(str(chat_id))
        if registro:
            conversation_id = registro.get("rcvs_chatwoot_conversation_id")
            source_id = registro.get("rcvs_chatwoot_source_id")
            if conversation_id and source_id:
                # Enviar la réplica del bot a la conversación para que el agente vea el diálogo
                try:
                    await cw.enviar_mensaje(source_id, conversation_id, texto)
                except Exception as e:
                    print(f"❌ Error al enviar mensaje del bot a Chatwoot: {e}")
    except Exception as e:
        print(f"❌ Error verificando registro en Supabase para reflejar bot en Chatwoot: {e}")

    return result
