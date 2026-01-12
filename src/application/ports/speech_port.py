from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, BinaryIO


class SpeechPort(ABC):
    """Port interface (hexagonal) para operaciones de Speech.

    Define los métodos mínimos que un adaptador de infraestructura debe implementar:
    - `file_to_stream(file_path)`: devolver un stream binario del fichero de audio.
    - `stream_to_text(stream, assumed_format)`: transcribir stream a texto.
    - `text_to_file(text, voice, out_filename)`: sintetizar texto a fichero de audio.
    """

    @abstractmethod
    def file_to_stream(self, file_path: str) -> BinaryIO:
        """Leer `file_path` y devolver un objeto file-like binario (por ejemplo `BytesIO`).

        Debe lanzar `FileNotFoundError` si el fichero no existe.
        """

    @abstractmethod
    def stream_to_text(self, stream: BinaryIO, assumed_format: str = "wav") -> Optional[str]:
        """Transcribir un stream binario a texto.

        - `stream`: objeto file-like en modo binario.
        - `assumed_format`: extensión/format hint (ej. "wav", "mp3").

        Devuelve la transcripción o `None` si no se reconoce audio.
        """

    @abstractmethod
    def text_to_file(self, text: str, voice: str, out_filename: str) -> None:
        """Sintetizar `text` usando la `voice` indicada y escribir el audio en `out_filename`.

        Debe lanzar una excepción en caso de error de síntesis.
        """

    @abstractmethod
    def text_to_stream(self, text: str, voice: str, format: str = "mp3"):
        """Sintetizar `text` usando la `voice` indicada y devolver un stream binario con el audio.

        - `format`: hint para el formato de salida (por ejemplo "mp3" o "wav").
        Debe devolver un file-like binario (por ejemplo `io.BytesIO`).
        """
