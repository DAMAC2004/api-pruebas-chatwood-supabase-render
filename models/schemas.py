from pydantic import BaseModel
from typing import Optional


# ── Supabase ──────────────────────────────────────────────────────────────────

class VerificarRegistroParams(BaseModel):
    """Query param para verificar si existe registro por chat_id de Telegram."""
    chat_id: str


class GenerarRegistroBody(BaseModel):
    """Body para crear registro en ambas tablas (caso 1 - primer mensaje)."""
    chat_id: str        # rmsgt_id_telegram_cvs
    mensaje: str        # rcvs_msg
    quien: str          # rcvs_who — username del usuario o "bot"


class GenerarRegistroMensajeBody(BaseModel):
    """Body para agregar solo un mensaje a registro_conversacion (caso 2+)."""
    chat_id: str        # para buscar el rmsgt_id relacionado
    mensaje: str        # rcvs_msg
    quien: str          # rcvs_who


class ActualizarRegistroBody(BaseModel):
    """Body para cambiar el modo de 'bot' a 'humano'."""
    chat_id: str        # identificador de la conversación a actualizar


# ── Telegram webhook ──────────────────────────────────────────────────────────

class TelegramChat(BaseModel):
    id: int

class TelegramFrom(BaseModel):
    username: Optional[str] = "desconocido"

class TelegramMessage(BaseModel):
    chat: TelegramChat
    from_: Optional[TelegramFrom] = None
    text: Optional[str] = ""

    class Config:
        # "from" es palabra reservada en Python, Telegram lo manda como "from"
        populate_by_name = True
        fields = {"from_": "from"}

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None


# ── Chatwoot webhook ──────────────────────────────────────────────────────────

class ChatwootSender(BaseModel):
    type: Optional[str] = ""

class ChatwootConversation(BaseModel):
    id: Optional[int] = None

class ChatwootWebhookPayload(BaseModel):
    event: Optional[str] = ""
    message_type: Optional[str] = ""
    content: Optional[str] = ""
    conversation: Optional[ChatwootConversation] = None
    sender: Optional[ChatwootSender] = None
