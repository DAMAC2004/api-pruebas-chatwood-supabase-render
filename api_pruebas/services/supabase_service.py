from core.config import supabase


# ── Tabla: registro_mensaje_telegram ─────────────────────────────────────────

def verificar_registro(chat_id: str) -> bool:
    """
    Busca si existe un registro en registro_mensaje_telegram
    con el chat_id de Telegram dado.
    Retorna True si existe, False si no.
    """
    response = (
        supabase.table("registro_mensaje_telegram")
        .select("rmsgt_id")
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .execute()
    )
    return len(response.data) > 0


def obtener_registro(chat_id: str) -> dict | None:
    """
    Retorna el registro completo de registro_mensaje_telegram
    para el chat_id dado, o None si no existe.
    """
    response = (
        supabase.table("registro_mensaje_telegram")
        .select("*")
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .single()
        .execute()
    )
    return response.data


def crear_registro_telegram(chat_id: str) -> dict:
    """
    Inserta una nueva fila en registro_mensaje_telegram.
    El modo default es 'bot' (definido en la BD).
    Retorna el registro creado.
    """
    response = (
        supabase.table("registro_mensaje_telegram")
        .insert({"rmsgt_id_telegram_cvs": chat_id})
        .execute()
    )
    return response.data[0]


def actualizar_modo_humano(chat_id: str) -> dict:
    """
    Cambia el campo rmsgt_id_modo de 'bot' a 'humano'
    para el registro con el chat_id indicado.
    Retorna el registro actualizado.
    """
    response = (
        supabase.table("registro_mensaje_telegram")
        .update({"rmsgt_id_modo": "humano"})
        .eq("rmsgt_id_telegram_cvs", chat_id)
        .execute()
    )
    return response.data[0]


# ── Tabla: registro_conversacion ──────────────────────────────────────────────

def crear_mensaje(rmsgt_id: int, mensaje: str, quien: str) -> dict:
    """
    Inserta un mensaje en registro_conversacion.
    - rmsgt_id: FK hacia registro_mensaje_telegram
    - mensaje:  contenido del texto
    - quien:    username del usuario o "bot"
    Retorna el registro creado.
    """
    response = (
        supabase.table("registro_conversacion")
        .insert({
            "rmsgt_id": rmsgt_id,
            "rcvs_msg": mensaje[:100],   # respetar el varchar(100) de la BD
            "rcvs_who": quien[:50],
        })
        .execute()
    )
    return response.data[0]


def obtener_mensajes(rmsgt_id: int) -> list:
    """
    Retorna todos los mensajes de una conversación ordenados por fecha.
    """
    response = (
        supabase.table("registro_conversacion")
        .select("*")
        .eq("rmsgt_id", rmsgt_id)
        .order("created_at")
        .execute()
    )
    return response.data
