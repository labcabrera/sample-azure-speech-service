import argparse
import importlib.util
import sys
from typing import Optional
import io


def load_speech_service():
    # Cargar SpeechService desde su ruta en `src/domain/services/speech_service.py`.
    path = "src/domain/services/speech_service.py"
    spec = importlib.util.spec_from_file_location("speech_service", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.SpeechService


def transcribe_file_with_service(file_path: str) -> Optional[str]:
    SpeechService = load_speech_service()
    svc = SpeechService()
    stream = svc.file_to_stream(file_path)
    # intentar inferir formato por extensión
    ext = file_path.split('.')[-1] if '.' in file_path else 'wav'
    return svc.stream_to_text(stream, assumed_format=ext)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transcribe a file using SpeechService.')
    parser.add_argument('file', nargs='?', default='output/output-es-ES-ElviraNeural.mp3', help='Path to audio file to transcribe')
    args = parser.parse_args()

    try:
        text = transcribe_file_with_service(args.file)
        if text:
            print('Transcription result:')
            print(text)
        else:
            print('No transcription returned.')
    except Exception as e:
        print(f'Error: {e}')
