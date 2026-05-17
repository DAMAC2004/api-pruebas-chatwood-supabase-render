import httpx
from core.config import (
    CHATWOOT_BASE_URL,
    CHATWOOT_API_TOKEN,
    CHATWOOT_ACCOUNT_ID,
    CHATWOOT_INBOX_ID,
)

HEADERS = {
    "Content-Type": "application/json",
    "api_access_token": CHATWOOT_API_TOKEN,
}

BASE = f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}"


async def crear_contacto(nombre: str, identificador: str) -> dict:
    """
    Crea un contacto en Chatwoot asociado al inbox API.
    Retorna la respuesta completa que incluye source_id.

    El source_id es el identificador de sesión del contacto
    y se usa para crear la conversación.
    """
    url = f"{BASE}/contacts"
    payload = {
        "name": nombre,
        "identifier": identificador,   # usamos el chat_id de Telegram como identificador único
        "inbox_id": int(CHATWOOT_INBOX_ID),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()


async def crear_conversacion(source_id: str) -> int:
    """
    Crea una nueva conversación en Chatwoot usando el source_id del contacto.
    Retorna el conversation_id.
    """
    url = f"{BASE}/conversations"
    payload = {
        "source_id": source_id,
        "inbox_id": int(CHATWOOT_INBOX_ID),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["id"]


async def enviar_mensaje_incoming(conversation_id: int, contenido: str) -> dict:
    """
    Envía un mensaje tipo 'incoming' (del usuario) a una conversación en Chatwoot.
    Esto es lo que verá el agente humano en el dashboard.
    """
    url = f"{BASE}/conversations/{conversation_id}/messages"
    payload = {
        "content": contenido,
        "message_type": "incoming",
        "private": False,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()


async def escalar_a_chatwoot(
    chat_id: str,
    username: str,
    mensaje_actual: str,
) -> int:
    """
    Flujo completo de escalado:
      1. Crea el contacto en Chatwoot
      2. Crea la conversación usando el source_id
      3. Envía el mensaje del usuario como 'incoming'

    Retorna el conversation_id de Chatwoot para guardarlo si es necesario.
    """
    # Paso 1 — contacto
    contacto_data = await crear_contacto(
        nombre=username,
        identificador=chat_id,
    )

    # El source_id viene dentro de contact_inboxes[0]
    source_id = contacto_data["contact_inboxes"][0]["source_id"]

    # Paso 2 — conversación
    conversation_id = await crear_conversacion(source_id)

    # Paso 3 — mensaje del usuario
    await enviar_mensaje_incoming(conversation_id, mensaje_actual)

    return conversation_id
