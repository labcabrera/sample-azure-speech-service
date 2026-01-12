from __future__ import annotations

import io
import os
import tempfile
from typing import Optional

from fastapi import FastAPI

from src.interfaces.http.rest_router import rest_router


app = FastAPI(title="Speech Service API")
app.include_router(rest_router)
