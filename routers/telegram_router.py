from fastapi import APIRouter, Request, Response, status
from models.schemas import TelegramUpdate
import services.supabase_service as db
import services.telegram_service as tg
import services.chatwoot_service as cw
import random
import asyncio

router = APIRouter(tags=["Telegram"])


@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """
    Webhook principal de Telegram. Maneja 3 casos:

    CASO 1 — Sin registro: primer mensaje del usuario.
      → Crea registro en Supabase (modo=bot)
      → Responde "Hola soy un bot"

    CASO 2 — Registro en modo 'bot': segundo mensaje, escalar.
      → Crea conversación en Chatwoot
      → Guarda conversation_id Y source_id en Supabase
      → Cambia modo a 'humano'
      → Avisa al usuario

    CASO 3 — Registro en modo 'humano': mensajes siguientes.
      → Usa el source_id Y conversation_id guardados en BD
      → Envía el mensaje a la conversación EXISTENTE en Chatwoot
      → No crea ni nuevas sesiones ni nuevas conversaciones
    """
    try:
        payload = await request.json()
        print("📨 Update recibido de Telegram:", payload)

        update = TelegramUpdate(**payload)

        if not update.message or not update.message.text:
            print("⚠️  Update sin mensaje de texto, ignorado.")
            return Response(status_code=status.HTTP_200_OK)

        chat_id  = str(update.message.chat.id)
        texto    = update.message.text
        username = update.message.from_.username if update.message.from_ else "desconocido"

        print(f"👤 Usuario: {username} | chat_id: {chat_id} | Mensaje: {texto}")

        registro = db.obtener_registro(chat_id)

        # ── CASO 1: no existe registro ────────────────────────────────────────
        if registro is None:
            print("🆕 Caso 1: primer mensaje, creando registro...")
            nuevo = db.crear_registro_telegram(chat_id)
            db.crear_mensaje(nuevo["rmsgt_id"], texto, username)

            await tg.enviar_mensaje(
                chat_id=update.message.chat.id,
                texto="👋 ¡Hola! Soy un bot. ¿En qué puedo ayudarte?\n\nEscríbeme otro mensaje para hablar con un agente humano.",
            )

        # ── CASO 2: registro en modo 'bot' → probabilidad de escalado ────────────
        elif registro["rmsgt_id_modo"] == "bot":
            print("🔁 Caso 2: modo bot, evaluando escalado...")
            db.crear_mensaje(registro["rmsgt_id"], texto, username)

            # Generar probabilidad aleatoria: 1-100
            probabilidad = random.randint(1, 100)
            print(f"🎲 Probabilidad generada: {probabilidad}")

            if probabilidad <= 40:
                print("✅ 40% activado: Escalando a humano...")
                
                # Simulación de bot procesando
                await tg.enviar_mensaje(
                    chat_id=update.message.chat.id,
                    texto="🤖 Procesando tu solicitud...",
                )
                await asyncio.sleep(2)
                
                await tg.enviar_mensaje(
                    chat_id=update.message.chat.id,
                    texto="👤 Conectando con un agente humano...",
                )
                await asyncio.sleep(1)
                
                # Ejecutar escalado a Chatwoot
                conversation_id, source_id = await cw.escalar_a_chatwoot(
                    chat_id=chat_id,
                    username=username,
                    mensaje_actual=texto,
                )

                # Guardar AMBOS: conversation_id y source_id
                db.actualizar_modo_humano(chat_id, conversation_id, source_id)
                print(f"✅ Guardado en BD | conversation_id: {conversation_id} | source_id: {source_id}")

                await tg.enviar_mensaje(
                    chat_id=update.message.chat.id,
                    texto="⏳ ¡Listo! Tu conversación está con un agente humano. En breve te atenderán.",
                )
            else:
                print("❌ 60% sin escalado: Continuando en modo bot...")
                await tg.enviar_mensaje(
                    chat_id=update.message.chat.id,
                    texto="🤖 Gracias por tu mensaje. Aunque por ahora sigo siendo un bot, tu mensaje ha sido registrado. Intenta escribir de nuevo.",
                )

        # ── CASO 3: modo 'humano' → reenviar a la conversación existente ──────
        else:
            print("💬 reenviando a conversación existente en Chatwoot...")
            db.crear_mensaje(registro["rmsgt_id"], texto, username)

            conversation_id = registro.get("rcvs_chatwoot_conversation_id")
            source_id       = registro.get("rcvs_chatwoot_source_id")

            if not conversation_id or not source_id:
                print("❌ Faltan conversation_id o source_id en BD.")
                return Response(status_code=status.HTTP_200_OK)

            # Usar el source_id original — el mismo con el que se creó la conversación
            await cw.enviar_mensaje(source_id, conversation_id, texto)
            print(f"✅ Mensaje reenviado a conversación {conversation_id}")

    except Exception as e:
        print(f"❌ Error en webhook de Telegram: {e}")

    return Response(status_code=status.HTTP_200_OK)
