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
        .single()
        .execute()
    )
    return response.data


def crear_registro_telegram(chat_id: str) -> dict:
    response = (
        supabase.table("registro_mensaje_telegram")
        .insert({"rmsgt_id_telegram_cvs": chat_id})
        .execute()
    )
    return response.data[0]


def actualizar_modo_humano(chat_id: str, chatwoot_conversation_id: int) -> dict:
    """
    Cambia el modo a 'humano' y guarda el conversation_id de Chatwoot.
    Así los siguientes mensajes del usuario van a la misma conversación.
    """
    response = (
        supabase.table("registro_mensaje_telegram")
        .update({
            "rmsgt_id_modo": "humano",
            "rcvs_chatwoot_conversation_id": chatwoot_conversation_id,
        })
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .execute()
    )
    return response.data[0]


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
