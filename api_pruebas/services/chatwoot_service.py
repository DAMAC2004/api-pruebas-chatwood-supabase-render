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


async def crear_contacto(nombre: str, identificador: str) -> int:
    """
    Paso 1: Crea el contacto en Chatwoot (sin inbox_id en el body).
    La API de Chatwoot no acepta inbox_id al crear el contacto;
    eso se maneja en el paso siguiente con contact_inboxes.
    Retorna el contact_id.
    """
    url = f"{BASE}/contacts"
    payload = {
        "name": nombre,
        "identifier": identificador,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        print(f"🔍 Chatwoot crear_contacto status: {response.status_code}")
        print(f"🔍 Chatwoot crear_contacto body: {response.text}")
        response.raise_for_status()
        data = response.json()
        return data["id"]


async def crear_contact_inbox(contact_id: int) -> str:
    """
    Paso 2a: Asocia el contacto a un inbox y obtiene el source_id.
    El source_id es el identificador de sesión necesario para crear la conversación.
    """
    url = f"{BASE}/contacts/{contact_id}/contact_inboxes"
    payload = {
        "inbox_id": int(CHATWOOT_INBOX_ID),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        print(f"🔍 Chatwoot contact_inbox status: {response.status_code}")
        print(f"🔍 Chatwoot contact_inbox body: {response.text}")
        response.raise_for_status()
        data = response.json()
        return data["source_id"]


async def crear_conversacion(source_id: str) -> int:
    """
    Paso 2b: Crea la conversación usando el source_id del contact_inbox.
    Retorna el conversation_id.
    """
    url = f"{BASE}/conversations"
    payload = {
        "source_id": source_id,
        "inbox_id": int(CHATWOOT_INBOX_ID),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        print(f"🔍 Chatwoot crear_conversacion status: {response.status_code}")
        print(f"🔍 Chatwoot crear_conversacion body: {response.text}")
        response.raise_for_status()
        data = response.json()
        return data["id"]


async def enviar_mensaje_incoming(conversation_id: int, contenido: str) -> dict:
    """
    Paso 3: Envía el mensaje del usuario como 'incoming' a la conversación.
    El agente humano lo verá en el dashboard de Chatwoot.
    """
    url = f"{BASE}/conversations/{conversation_id}/messages"
    payload = {
        "content": contenido,
        "message_type": "incoming",
        "private": False,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        print(f"🔍 Chatwoot enviar_mensaje status: {response.status_code}")
        response.raise_for_status()
        return response.json()


async def escalar_a_chatwoot(
    chat_id: str,
    username: str,
    mensaje_actual: str,
) -> int:
    """
    Flujo completo de escalado a Chatwoot:
      1. Crear contacto                → obtiene contact_id
      2a. Crear contact_inbox          → obtiene source_id
      2b. Crear conversación           → obtiene conversation_id
      3. Enviar mensaje como incoming  → el agente lo ve en el dashboard

    Retorna el conversation_id.
    """
    print(f"🚀 Iniciando escalado a Chatwoot para chat_id: {chat_id}")

    # Paso 1
    contact_id = await crear_contacto(nombre=username, identificador=chat_id)
    print(f"✅ Contacto creado con ID: {contact_id}")

    # Paso 2a
    source_id = await crear_contact_inbox(contact_id)
    print(f"✅ source_id obtenido: {source_id}")

    # Paso 2b
    conversation_id = await crear_conversacion(source_id)
    print(f"✅ Conversación creada con ID: {conversation_id}")

    # Paso 3
    await enviar_mensaje_incoming(conversation_id, mensaje_actual)
    print(f"✅ Mensaje enviado a conversación {conversation_id}")

    return conversation_id
