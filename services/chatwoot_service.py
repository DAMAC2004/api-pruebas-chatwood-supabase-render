import httpx
from core.config import CHATWOOT_BASE_URL, CHATWOOT_INBOX_ID

HEADERS = {"Content-Type": "application/json"}
BASE = f"{CHATWOOT_BASE_URL}/public/api/v1/inboxes/{CHATWOOT_INBOX_ID}"


async def crear_contacto(nombre: str, identificador: str) -> tuple[str, str]:
    """
    Crea el contacto en el inbox API.
    Retorna (source_id, pubsub_token).
    El source_id es el identificador de sesión — debe guardarse para
    enviar mensajes a la conversación que se cree con esta sesión.
    """
    url = f"{BASE}/contacts"
    payload = {"name": nombre, "identifier": identificador}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS, timeout=10)
        print(f"🔍 [crear_contacto] status: {response.status_code} | body: {response.text}")
        response.raise_for_status()
        data = response.json()
        return data["source_id"], data.get("pubsub_token", "")


async def crear_conversacion(source_id: str) -> int:
    """
    Crea la conversación para el contacto identificado por source_id.
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
    Envía un mensaje a la conversación.
    IMPORTANTE: el source_id debe ser el mismo con el que se creó
    la conversación. Un source_id diferente da 404.
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
) -> tuple[int, str]:
    """
    Flujo completo de escalado. Retorna (conversation_id, source_id).
    Ambos deben guardarse en BD para usarlos en mensajes posteriores.
    """
    print(f"🚀 Escalando a Chatwoot | chat_id: {chat_id} | usuario: {username}")

    source_id, _ = await crear_contacto(nombre=username, identificador=chat_id)
    print(f"✅ Contacto creado | source_id: {source_id}")

    conversation_id = await crear_conversacion(source_id)
    print(f"✅ Conversación creada | conversation_id: {conversation_id}")

    await enviar_mensaje(source_id, conversation_id, mensaje_actual)
    print(f"✅ Mensaje enviado a conversación {conversation_id}")

    return conversation_id, source_id
