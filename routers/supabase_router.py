from fastapi import APIRouter, HTTPException, Query
from models.schemas import (
    GenerarRegistroBody,
    GenerarRegistroMensajeBody,
    ActualizarRegistroBody,
)
import services.supabase_service as db

router = APIRouter(prefix="/prueba/supabase", tags=["Supabase"])


# ── GET prueba/supabase/verificar-registro ────────────────────────────────────
@router.get("/verificar-registro")
def verificar_registro(chat_id: str = Query(..., description="chat.id de Telegram")):
    """
    Verifica si existe un registro en registro_mensaje_telegram
    para el chat_id recibido.

    - Retorna `exists: true` si ya hay registro → flujo Caso 2
    - Retorna `exists: false` si no hay registro → flujo Caso 1
    """
    try:
        existe = db.verificar_registro(chat_id)
        return {"exists": existe, "chat_id": chat_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST prueba/supabase/generar-registro ─────────────────────────────────────
@router.post("/generar-registro", status_code=201)
def generar_registro(body: GenerarRegistroBody):
    """
    Caso 1 — primer mensaje del usuario.
    Inserta en ambas tablas:
      1. registro_mensaje_telegram  (modo = 'bot' por defecto)
      2. registro_conversacion      (el mensaje inicial)
    """
    try:
        # Verificar que no exista ya (doble seguridad)
        if db.verificar_registro(body.chat_id):
            raise HTTPException(
                status_code=409,
                detail="Ya existe un registro para este chat_id. Usa actualizar-registro."
            )

        # 1. Crear registro principal
        registro = db.crear_registro_telegram(body.chat_id)
        rmsgt_id = registro["rmsgt_id"]

        # 2. Guardar el mensaje inicial
        mensaje = db.crear_mensaje(rmsgt_id, body.mensaje, body.quien)

        return {
            "message": "Registro creado exitosamente",
            "registro": registro,
            "primer_mensaje": mensaje,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST prueba/supabase/generar-registro-mensaje ─────────────────────────────
@router.post("/generar-registro-mensaje", status_code=201)
def generar_registro_mensaje(body: GenerarRegistroMensajeBody):
    """
    Solo inserta un mensaje en registro_conversacion.
    Úsalo cuando el registro principal ya existe (Caso 2 en adelante).
    """
    try:
        # Obtener el rmsgt_id del registro principal
        registro = db.obtener_registro(body.chat_id)
        if not registro:
            raise HTTPException(
                status_code=404,
                detail="No existe registro para este chat_id. Usa generar-registro primero."
            )

        mensaje = db.crear_mensaje(registro["rmsgt_id"], body.mensaje, body.quien)

        return {
            "message": "Mensaje registrado exitosamente",
            "mensaje": mensaje,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── PATCH prueba/supabase/actualizar-registro ─────────────────────────────────
@router.patch("/actualizar-registro")
def actualizar_registro(body: ActualizarRegistroBody):
    """
    Cambia el modo de la conversación de 'bot' → 'humano'.
    Se ejecuta cuando se va a escalar la conversación a Chatwoot.
    """
    try:
        if not db.verificar_registro(body.chat_id):
            raise HTTPException(
                status_code=404,
                detail="No existe registro para este chat_id."
            )

        registro_actualizado = db.actualizar_modo_humano(body.chat_id)

        return {
            "message": "Modo actualizado a 'humano'",
            "registro": registro_actualizado,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
