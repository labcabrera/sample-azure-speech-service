import os
import io
import tempfile
from typing import Optional, Iterable

import azure.cognitiveservices.speech as speechsdk

try:
	from ..application.ports.speech_port import SpeechPort
except Exception:
	# Fallback when module executed as script or package layout differs
	try:
		from src.application.ports.speech_port import SpeechPort
	except Exception:
		SpeechPort = object


def _get_speech_config(speech_key: Optional[str] = None, region_or_endpoint: Optional[str] = None) -> speechsdk.SpeechConfig:
	key = speech_key or os.environ.get('SPEECH_KEY')
	region_or_endpoint = region_or_endpoint or os.environ.get('SPEECH_REGION') or os.environ.get('SPEECH_ENDPOINT')

	if not key or not region_or_endpoint:
		raise ValueError("Please set SPEECH_KEY and SPEECH_REGION (or SPEECH_ENDPOINT) environment variables or pass them to SpeechService.")

	if region_or_endpoint.startswith('http'):
		return speechsdk.SpeechConfig(subscription=key, endpoint=region_or_endpoint)
	else:
		return speechsdk.SpeechConfig(subscription=key, region=region_or_endpoint)


class SpeechService:
	"""Servicio ligero para convertir audio a texto y para obtener un stream desde un fichero.

	- `file_to_stream(file_path)` devuelve un `io.BytesIO` con el contenido del fichero.
	- `stream_to_text(stream)` devuelve la transcripción (o `None`) usando Azure Speech.

	Esta implementación usa un fichero temporal para pasar el audio al SDK de Azure de forma
	robusta (evita dependencias sobre formatos de stream específicos).
	"""

	def __init__(self, speech_key: Optional[str] = None, region_or_endpoint: Optional[str] = None, languages: Optional[Iterable[str]] = None):
		self.speech_config = _get_speech_config(speech_key, region_or_endpoint)
		# Idiomas para detección automática si se desea
		self.languages = list(languages) if languages is not None else ["es-ES", "ca-ES"]

	def file_to_stream(self, file_path: str) -> io.BytesIO:
		"""Leer `file_path` en modo binario y devolver un `BytesIO` listo para usarse.

		Lanza `FileNotFoundError` si el fichero no existe.
		"""
		if not os.path.exists(file_path):
			raise FileNotFoundError(f"Audio file not found: {file_path}")

		with open(file_path, "rb") as fh:
			data = fh.read()

		return io.BytesIO(data)

	def stream_to_text(self, stream: io.BytesIO, assumed_format: str = "wav") -> Optional[str]:
		"""Transcribe un stream binario a texto.

		- `stream` debe ser un objeto file-like en modo binario (por ejemplo `BytesIO`).
		- `assumed_format` es el sufijo para el fichero temporal ("wav", "mp3"...),
		  por defecto "wav".

		Devuelve la cadena reconocida o `None` si no hubo reconocimiento.
		"""
		# Escribe a fichero temporal y reutiliza la lógica de AudioConfig(filename=...)
		suffix = f'.{assumed_format.lstrip(".")}' if assumed_format else ''
		with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
			tmp.write(stream.read())
			tmp.flush()
			tmp_name = tmp.name

		try:
			audio_input = speechsdk.audio.AudioConfig(filename=tmp_name)
			# Usamos detección automática de idioma por defecto (si se proporcionan idiomas)
			adc = None
			if self.languages:
				adc = speechsdk.AutoDetectSourceLanguageConfig(languages=self.languages)
				recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_input, auto_detect_source_language_config=adc)
			else:
				recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_input)

			result = recognizer.recognize_once_async().get()

			# Debugging info (keeps behavior similar to sample-speech-to-text)
			# print(f"[DEBUG] result.reason = {result.reason}")
			# print(f"[DEBUG] result.text = {getattr(result, 'text', None)}")

			if result.reason == speechsdk.ResultReason.RecognizedSpeech:
				return result.text
			else:
				return None
		finally:
			try:
				os.unlink(tmp_name)
			except Exception:
				pass

	def text_to_file(self, text: str, voice: str, out_filename: str) -> None:
		"""Síntesis de texto a fichero usando Azure Speech.

		- `text`: texto a sintetizar
		- `voice`: nombre de la voz (p.ej. "es-ES-ElviraNeural")
		- `out_filename`: ruta de salida (mp3/wav)
		"""
		audio_config = speechsdk.audio.AudioOutputConfig(filename=out_filename)
		# Clone speech_config to avoid mutating caller's config
		sc = _get_speech_config()
		sc.speech_synthesis_voice_name = voice
		synthesizer = speechsdk.SpeechSynthesizer(speech_config=sc, audio_config=audio_config)
		result = synthesizer.speak_text_async(text).get()

		if result.reason == speechsdk.ResultReason.Canceled:
			cd = result.cancellation_details
			raise RuntimeError(f"TTS canceled: {getattr(cd, 'reason', None)} - {getattr(cd, 'error_details', None)}")


class AzureSpeechServiceAdapter(SpeechPort):
	"""Adaptador de infraestructura para Azure Speech que implementa el port `SpeechPort`.

	Esta clase delega en la implementación local `SpeechService` y adapta
	la interfaz al puerto definido en `src/infrastructure/ports/speech_port.py`.
	"""

	def __init__(self, speech_key: Optional[str] = None, region_or_endpoint: Optional[str] = None, languages: Optional[Iterable[str]] = None):
		self._svc = SpeechService(speech_key=speech_key, region_or_endpoint=region_or_endpoint, languages=languages)

	def file_to_stream(self, file_path: str) -> io.BytesIO:
		return self._svc.file_to_stream(file_path)

	def stream_to_text(self, stream: io.BytesIO, assumed_format: str = "wav") -> Optional[str]:
		return self._svc.stream_to_text(stream, assumed_format=assumed_format)

	def text_to_file(self, text: str, voice: str, out_filename: str) -> None:
		return self._svc.text_to_file(text, voice, out_filename)

