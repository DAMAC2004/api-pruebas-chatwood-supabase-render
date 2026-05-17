import httpx
from core.config import (
    CHATWOOT_BASE_URL,
    CHATWOOT_INBOX_ID,
)

# ── Client APIs de Chatwoot ───────────────────────────────────────────────────
# Estas APIs usan el inbox_identifier en la URL, NO el api_access_token.
# Ruta base: /public/api/v1/inboxes/{inbox_identifier}/...
# El CHATWOOT_INBOX_ID aquí es el inbox_identifier del canal API (string alfanumérico
# que se obtiene en Chatwoot → Settings → Inboxes → tu inbox → Configuration).

HEADERS = {"Content-Type": "application/json"}
BASE = f"{CHATWOOT_BASE_URL}/public/api/v1/inboxes/{CHATWOOT_INBOX_ID}"


async def crear_contacto(nombre: str, identificador: str) -> tuple[str, str]:
    """
    Paso 1: Crea el contacto en el inbox API.
    Endpoint: POST /public/api/v1/inboxes/{inbox_identifier}/contacts

    Retorna (source_id, pubsub_token).
    El source_id se usa como contact_identifier en los siguientes pasos.
    """
    url = f"{BASE}/contacts"
    payload = {
        "name": nombre,
        "identifier": identificador,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        print(f"🔍 [crear_contacto] status: {response.status_code} | body: {response.text}")
        response.raise_for_status()
        data = response.json()
        return data["source_id"], data.get("pubsub_token", "")


async def crear_conversacion(source_id: str) -> int:
    """
    Paso 2: Crea la conversación para el contacto.
    Endpoint: POST /public/api/v1/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations

    Retorna el conversation_id.
    """
    url = f"{BASE}/contacts/{source_id}/conversations"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={}, headers=HEADERS, timeout=10)
        print(f"🔍 [crear_conversacion] status: {response.status_code} | body: {response.text}")
        response.raise_for_status()
        data = response.json()
        return data["id"]


async def enviar_mensaje(source_id: str, conversation_id: int, contenido: str) -> dict:
    """
    Paso 3: Envía el mensaje del usuario a la conversación.
    Endpoint: POST /public/api/v1/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/messages

    El agente lo verá en el dashboard de Chatwoot como mensaje entrante.
    """
    url = f"{BASE}/contacts/{source_id}/conversations/{conversation_id}/messages"
    payload = {"content": contenido}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        print(f"🔍 [enviar_mensaje] status: {response.status_code} | body: {response.text}")
        response.raise_for_status()
        return response.json()


async def escalar_a_chatwoot(
    chat_id: str,
    username: str,
    mensaje_actual: str,
) -> int:
    """
    Flujo completo de escalado usando las Client APIs de Chatwoot:

      1. POST /contacts                          → obtiene source_id
      2. POST /contacts/{source_id}/conversations → obtiene conversation_id
      3. POST /contacts/{source_id}/conversations/{id}/messages → envía mensaje

    Retorna el conversation_id de Chatwoot.
    """
    print(f"🚀 Escalando a Chatwoot | chat_id: {chat_id} | usuario: {username}")

    source_id, _ = await crear_contacto(nombre=username, identificador=chat_id)
    print(f"✅ Contacto creado | source_id: {source_id}")

    conversation_id = await crear_conversacion(source_id)
    print(f"✅ Conversación creada | conversation_id: {conversation_id}")

    await enviar_mensaje(source_id, conversation_id, mensaje_actual)
    print(f"✅ Mensaje enviado a conversación {conversation_id}")

    return conversation_id
