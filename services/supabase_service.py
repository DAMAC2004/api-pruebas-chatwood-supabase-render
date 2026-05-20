from core.config import supabase


# ── Tabla: registro_mensaje_telegram ─────────────────────────────────────────

def verificar_registro(chat_id: str) -> bool:
    response = (
        supabase.table("registro_mensaje_telegram")
        .select("rmsgt_id")
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .execute()
    )
    return len(response.data) > 0


def obtener_registro(chat_id: str) -> dict | None:
    response = (
        supabase.table("registro_mensaje_telegram")
        .select("*")
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def crear_registro_telegram(chat_id: str) -> dict:
    response = (
        supabase.table("registro_mensaje_telegram")
        .insert({"rmsgt_id_telegram_cvs": chat_id})
        .execute()
    )
    return response.data[0]


def actualizar_modo_humano(
    chat_id: str,
    chatwoot_conversation_id: int,
    chatwoot_source_id: str,
) -> dict:
    """
    Cambia el modo a 'humano' y guarda el conversation_id Y el source_id
    de Chatwoot. Ambos son necesarios para enviar mensajes a esa misma
    conversación desde el Caso 3.
    """
    response = (
        supabase.table("registro_mensaje_telegram")
        .update({
            "rmsgt_id_modo": "humano",
            "rcvs_chatwoot_conversation_id": chatwoot_conversation_id,
            "rcvs_chatwoot_source_id": chatwoot_source_id,
        })
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .execute()
    )
    return response.data[0]


def actualizar_modo_bot(chat_id: str) -> dict | None:
    """
    Cambia el modo a 'bot' para el registro identificado por `chat_id`.
    Retorna el registro actualizado o None si no se encontró ninguno.
    """
    response = (
        supabase.table("registro_mensaje_telegram")
        .update({"rmsgt_id_modo": "bot"})
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .execute()
    )
    return response.data[0] if response.data else None


def guardar_ids_chatwoot(chat_id: str, conversation_id: int, source_id: str) -> dict | None:
    """
    Guarda los ids de Chatwoot (conversation_id y source_id) en el registro
    asociado a `chat_id` sin modificar el campo `rmsgt_id_modo`.
    Retorna el registro actualizado o None si no existe.
    """
    response = (
        supabase.table("registro_mensaje_telegram")
        .update({
            "rcvs_chatwoot_conversation_id": conversation_id,
            "rcvs_chatwoot_source_id": source_id,
        })
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .execute()
    )
    return response.data[0] if response.data else None


def set_modo_humano(chat_id: str) -> dict | None:
    """
    Actualiza solamente el campo `rmsgt_id_modo` a 'humano' para el registro
    identificado por `chat_id`.
    """
    response = (
        supabase.table("registro_mensaje_telegram")
        .update({"rmsgt_id_modo": "humano"})
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .execute()
    )
    return response.data[0] if response.data else None


# ── Tabla: registro_conversacion ──────────────────────────────────────────────

def crear_mensaje(rmsgt_id: int, mensaje: str, quien: str) -> dict:
    response = (
        supabase.table("registro_conversacion")
        .insert({
            "rmsgt_id": rmsgt_id,
            "rcvs_msg": mensaje[:100],
            "rcvs_who": quien[:50],
        })
        .execute()
    )
    return response.data[0]


def obtener_mensajes(rmsgt_id: int) -> list:
    response = (
        supabase.table("registro_conversacion")
        .select("*")
        .eq("rmsgt_id", rmsgt_id)
        .order("created_at")
        .execute()
    )
    return response.data
