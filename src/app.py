from __future__ import annotations

import io
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel


# Import adapter (try package-style import, fallback to relative)
try:
    from src.infrastructure.azure_speech_service_adapter import AzureSpeechServiceAdapter
except Exception:
    try:
        from infrastructure.azure_speech_service_adapter import AzureSpeechServiceAdapter
    except Exception:
        raise


app = FastAPI(title="Speech Service API")

# Initialize adapter (reads SPEECH_KEY / SPEECH_REGION from env if not provided)
adapter = AzureSpeechServiceAdapter()


class TTSRequest(BaseModel):
    text: str
    voice: str = "es-ES-ElviraNeural"
    format: str = "mp3"


@app.post("/api/v1/speech-to-text")
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


@app.post("/api/v1/text-to-speech")
async def text_to_speech(req: TTSRequest):
    """Recibe JSON con `text`, `voice` y `format` y devuelve el audio sintetizado como stream."""
    suffix = ".mp3" if req.format.lower() == "mp3" else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        out_name = tmp.name

    try:
        adapter.text_to_file(req.text, req.voice, out_name)

        def iterfile(path: str):
            with open(path, "rb") as fh:
                while True:
                    chunk = fh.read(8192)
                    if not chunk:
                        break
                    yield chunk

        media_type = "audio/mpeg" if suffix == ".mp3" else "audio/wav"
        headers = {"Content-Disposition": f"attachment; filename=output{suffix}"}
        return StreamingResponse(iterfile(out_name), media_type=media_type, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.unlink(out_name)
        except Exception:
            pass
