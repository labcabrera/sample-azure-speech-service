from __future__ import annotations

import io
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from src.infrastructure.adapters.azure_speech_service_adapter import AzureSpeechServiceAdapter

rest_router = APIRouter()
adapter = AzureSpeechServiceAdapter()

class TTSRequest(BaseModel):
    text: str = "Va a subir la marea, y se lo va a llevar todo\nNo veas si noto la fuerza\nYo creo que soy un toro\n\nDate prisa, que ya está aquí\nHay tormenta y yo me tiro al mar\nMe abandono no me voy a ahogar\nY ahora arriba soy el huracán"
    voice: str = "es-ES-ElviraNeural"
    format: str = "mp3"

@rest_router.post(
    "/api/v1/speech-to-text",
    tags=["Speech"],
    summary="Transcribe audio a texto",
    operation_id="speech_to_text",
)
async def speech_to_text(file: UploadFile = File(...), assumed_format: Optional[str] = Form("wav")):
    """Recibe un fichero de audio y devuelve la transcripción.

    - Form field `assumed_format` es opcional (ej: "wav", "mp3").
    """
    try:
        content = await file.read()
        stream = io.BytesIO(content)
        text = adapter.stream_to_text(stream, assumed_format=assumed_format)
        if text is None:
            return JSONResponse(status_code=204, content={})
        return {"text": text}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@rest_router.post(
    "/api/v1/text-to-speech",
    tags=["Speech"],
    summary="Sintetiza texto a audio",
    operation_id="text_to_speech",
)
async def text_to_speech(req: TTSRequest):
    """Recibe JSON con `text`, `voice` y `format` y devuelve el audio sintetizado como stream."""
    try:
        stream = adapter.text_to_stream(req.text, req.voice, format=req.format)

        def iter_bytes(io_stream: io.BytesIO):
            io_stream.seek(0)
            while True:
                chunk = io_stream.read(8192)
                if not chunk:
                    break
                yield chunk

        media_type = "audio/mpeg" if req.format.lower() == "mp3" else "audio/wav"
        headers = {"Content-Disposition": f"attachment; filename=output.{req.format.lower()}"}
        return StreamingResponse(iter_bytes(stream), media_type=media_type, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@rest_router.get(
    "/api/v1/voices",
    tags=["Speech"],
    summary="Lista las voces disponibles",
    operation_id="available_voices",
)
async def available_voices(language: Optional[str] = None):
    """Devuelve las voces disponibles. Query param `language` filtra por código (ej. 'es')."""
    try:
        voices = adapter.available_voices(language)
        if voices is None:
            # No hay fichero local y la operación puede no ser aplicable
            return JSONResponse(status_code=204, content={})
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
