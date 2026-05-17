from fastapi import APIRouter, Request, Response, status
from models.schemas import TelegramUpdate
import services.supabase_service as db
import services.telegram_service as tg
import services.chatwoot_service as cw

router = APIRouter(tags=["Telegram"])


@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """
    Punto de entrada principal del bot de Telegram.

    Telegram hace POST aquí cada vez que el usuario manda un mensaje.
    IMPORTANTE: siempre debe retornar 200 OK, incluso si hay errores
    internos, para evitar que Telegram reintente la petición en bucle.

    Flujo:
      - Caso 1 (sin registro): crea registro → responde "Hola soy un bot"
      - Caso 2 (con registro): cambia modo → escala a Chatwoot → avisa al usuario
    """
    try:
        payload = await request.json()
        print("📨 Update recibido de Telegram:", payload)

        update = TelegramUpdate(**payload)

        # Ignorar actualizaciones sin mensaje de texto
        if not update.message or not update.message.text:
            print("⚠️  Update sin mensaje de texto, ignorado.")
            return Response(status_code=status.HTTP_200_OK)

        chat_id   = str(update.message.chat.id)
        texto     = update.message.text
        username  = update.message.from_.username if update.message.from_ else "desconocido"

        print(f"👤 Usuario: {username} | chat_id: {chat_id} | Mensaje: {texto}")

        existe = db.verificar_registro(chat_id)

        # ── CASO 1: no hay registro ───────────────────────────────────────────
        if not existe:
            print("🆕 Caso 1: primer mensaje, creando registro...")

            registro = db.crear_registro_telegram(chat_id)
            db.crear_mensaje(registro["rmsgt_id"], texto, username)

            await tg.enviar_mensaje(
                chat_id=update.message.chat.id,
                texto="👋 ¡Hola! Soy un bot. ¿En qué puedo ayudarte?\n\nEscríbeme otro mensaje para hablar con un agente humano.",
            )

        # ── CASO 2: ya hay registro → escalar a humano ────────────────────────
        else:
            print("🔁 Caso 2: registro existente, escalando a humano...")

            registro = db.obtener_registro(chat_id)
            db.crear_mensaje(registro["rmsgt_id"], texto, username)

            # Cambiar modo a humano en BD
            db.actualizar_modo_humano(chat_id)

            # Avisar al usuario
            await tg.enviar_mensaje(
                chat_id=update.message.chat.id,
                texto="⏳ Tu conversación está siendo escalada a un agente humano. En breve te atenderán.",
            )

            # Escalar a Chatwoot: crea contacto → conversación → mensaje
            conversation_id = await cw.escalar_a_chatwoot(
                chat_id=chat_id,
                username=username,
                mensaje_actual=texto,
            )
            print(f"✅ Conversación creada en Chatwoot con ID: {conversation_id}")

    except Exception as e:
        # Logueamos el error pero devolvemos 200 para que Telegram no reintente
        print(f"❌ Error en webhook de Telegram: {e}")

    # Siempre 200 OK
    return Response(status_code=status.HTTP_200_OK)
