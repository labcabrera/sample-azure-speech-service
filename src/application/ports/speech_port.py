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

    @abstractmethod
    def available_voices(self, language_code: Optional[str] = None) -> Optional[list]:
        """Devuelve la lista de voces disponibles.

        - `language_code`: si se proporciona, filtra por código de idioma (p.ej. 'es', 'ca').
        Devuelve una lista de diccionarios con claves `name`, `locale`, `gender` y `voice_type`.
        """
        # Intentar leer una lista pre-generada desde el fichero `available-voices.txt` en la raíz del repo.
        import re
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[2]
        voices_file = repo_root / 'available-voices.txt'
        if not voices_file.exists():
            return None

        voices = []
        section = None
        entry_re = re.compile(r"^-\s*(?P<display>.*?)\s*\((?P<locale1>[^,]+),\s*(?P<name>[^)]+)\)\s*\((?P<locale2>[^)]+)\)\s*-\s*(?P<gender>[^-]+)\s*-\s*(?P<voice_type>\S+)")
        for line in voices_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line.startswith("Available voices for language"):
                # extraer código de idioma si está presente
                m = re.search(r"'(?P<lang>[^']+)'", line)
                section = m.group('lang') if m else None
                continue
            if not line.startswith("-"):
                continue
            m = entry_re.match(line)
            if not m:
                # fallback: intentar parseo simple
                parts = [p.strip() for p in line.lstrip('-').split(' - ')]
                if not parts:
                    continue
                display = parts[0]
                voices.append({
                    'name': display,
                    'locale': section,
                    'gender': parts[1] if len(parts) > 1 else None,
                    'voice_type': parts[2] if len(parts) > 2 else None,
                })
                continue

            name = m.group('name').strip()
            locale = m.group('locale2').strip()
            gender = m.group('gender').strip()
            voice_type = m.group('voice_type').strip()
            # si se solicitó filtro por idioma, comprobar
            if language_code and not locale.startswith(language_code):
                continue
            voices.append({
                'name': name,
                'locale': locale,
                'gender': gender,
                'voice_type': voice_type,
            })

        return voices

