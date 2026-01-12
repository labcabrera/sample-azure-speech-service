from __future__ import annotations

import io
import os
import tempfile
from typing import Optional

from fastapi import FastAPI

from src.interfaces.http.rest_router import rest_router


openapi_tags = [
	{
		"name": "Speech",
		"description": "Operaciones de Speech: transcripción y síntesis (speech-to-text, text-to-speech).",
	}
]

app = FastAPI(
	title="Azure Speech API",
	description="API REST que expone operaciones de reconocimiento y síntesis de voz basadas en Azure Speech.",
	version="0.1.0",
	openapi_url="/api/v1/openapi.json",
	docs_url="/docs",
	redoc_url="/redoc",
	openapi_tags=openapi_tags,
)

app.include_router(rest_router)
