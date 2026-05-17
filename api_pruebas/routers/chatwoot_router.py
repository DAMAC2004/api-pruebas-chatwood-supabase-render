from fastapi import APIRouter, Request, Response, status
from models.schemas import ChatwootWebhookPayload
import services.supabase_service as db
import services.telegram_service as tg

router = APIRouter(tags=["Chatwoot"])


@router.post("/chatwoot-webhook")
async def chatwoot_webhook(request: Request):
    """
    Recibe eventos del canal API de Chatwoot.

    Chatwoot hace POST aquí cuando ocurre cualquier evento en el inbox.
    Solo procesamos mensajes tipo 'outgoing' (respuestas del agente humano)
    para reenviarlos al usuario en Telegram.

    Payload relevante de Chatwoot:
      - event:        "message_created"
      - message_type: "outgoing" (agente) | "incoming" (usuario, los ignoramos)
      - content:      texto del mensaje del agente
      - conversation.id: ID de la conversación en Chatwoot
    """
    try:
        payload = await request.json()
        print("📨 Evento recibido de Chatwoot:", payload)

        data = ChatwootWebhookPayload(**payload)

        # Solo procesamos mensajes nuevos tipo 'outgoing' del agente
        if data.event != "message_created":
            print(f"⚠️  Evento '{data.event}' ignorado.")
            return Response(status_code=status.HTTP_200_OK)

        if data.message_type != "outgoing":
            print(f"⚠️  Mensaje tipo '{data.message_type}' ignorado (solo procesamos outgoing).")
            return Response(status_code=status.HTTP_200_OK)

        if not data.content:
            print("⚠️  Mensaje sin contenido, ignorado.")
            return Response(status_code=status.HTTP_200_OK)

        print(f"✉️  Mensaje del agente: {data.content}")

        # ── Buscar el chat_id de Telegram correspondiente ─────────────────────
        # Chatwoot usa el 'identifier' del contacto, que nosotros seteamos como chat_id.
        # Lo recuperamos desde el payload completo si está disponible.
        raw = await request.json() if False else payload   # ya lo tenemos en payload
        chat_id = _extraer_chat_id_de_payload(raw)

        if not chat_id:
            print("❌ No se pudo obtener el chat_id del payload de Chatwoot.")
            return Response(status_code=status.HTTP_200_OK)

        # Reenviar la respuesta del agente al usuario en Telegram
        await tg.enviar_mensaje(
            chat_id=chat_id,
            texto=f"💬 <b>Agente:</b> {data.content}",
        )
        print(f"✅ Mensaje reenviado a Telegram chat_id: {chat_id}")

    except Exception as e:
        print(f"❌ Error en webhook de Chatwoot: {e}")

    return Response(status_code=status.HTTP_200_OK)


def _extraer_chat_id_de_payload(payload: dict) -> str | None:
    """
    Intenta extraer el chat_id de Telegram desde el payload de Chatwoot.
    Chatwoot incluye el 'identifier' del contacto en el campo:
      payload -> conversation -> meta -> sender -> identifier
    o en:
      payload -> sender -> identifier (según la versión de Chatwoot)
    """
    try:
        # Intento 1: conversation.meta.sender.identifier
        return payload["conversation"]["meta"]["sender"]["identifier"]
    except (KeyError, TypeError):
        pass

    try:
        # Intento 2: sender.identifier
        return payload["sender"]["identifier"]
    except (KeyError, TypeError):
        pass

    return None
