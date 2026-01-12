import os
import time
import azure.cognitiveservices.speech as speechsdk

es_available_voices = [
    "es-ES-ElviraNeural",
    "es-ES-AlvaroNeural",
    "es-ES-AbrilNeural",
    "es-ES-ArnauNeural",
    "es-ES-DarioNeural",
    "es-ES-EliasNeural",
    "es-ES-EstrellaNeural",
    "es-ES-IreneNeural",
    "es-ES-LaiaNeural",
    "es-ES-LiaNeural",
    "es-ES-NilNeural",
    "es-ES-SaulNeural",
    "es-ES-TeoNeural",
    "es-ES-TrianaNeural",
    "es-ES-VeraNeural",
    "es-ES-XimenaNeural",
    "es-ES-Tristan:DragonHDLatestNeural",
    "es-ES-Ximena:DragonHDLatestNeural"
]

ca_available_voices = [
    "ca-ES-JoanaNeural",
    "ca-ES-EnricNeural",
    "ca-ES-AlbaNeural"
]

eu_available_voices = [
    "eu-ES-AinhoaNeural",
    "eu-ES-AnderNeural"
]

gl_available_voices = [
    "gl-ES-SabelaNeural",
    "gl-ES-RoiNeural"
]

import importlib.util
import sys


def load_speech_service():
    path = "src/domain/services/speech_service.py"
    spec = importlib.util.spec_from_file_location("speech_service", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.SpeechService


SpeechService = load_speech_service()
svc = SpeechService()

text_es = "El número de teléfono de la oficina Avenida de las Pruebas es seis cinco cinco, cuatro dos, tres uno, uno cuatro. Se lo repito. Seis cinco cinco, cuatro dos, tres uno, uno cuatro."
text_ca = "El número de telèfon de l'oficina Avinguda de les Proves és sis cinc cinc, quatre dos, tres un, un quatre. Li ho repeteixo. Sis cinc cinc, quatre dos, tres un, un quatre."
text_eu = "Avenida de las Pruebas bulegoko telefono zenbakia sei bost bost, lau bi, hiru bat, bat lau da. Errepikatuko dut. Sei bost bost, lau bi, hiru bat, bat lau."
text_gl = "O número de teléfono da oficina da Avenida de las Pruebas é seis cinco cinco, catro dous, tres un, un catro. Repetireino. Seis cinco cinco, catro dous, tres un, un catro."


def create_mp3_file(text: str, voice: str):
    out = f"output/output-{voice}.mp3"
    print(f"Generating {out}...")
    svc.text_to_file(text, voice, out)
    print(f"Saved {out}")


for voice in es_available_voices:
    print(f"Testing voice: {voice}")
    create_mp3_file(text_es, voice)
    print(f"Finished testing voice: {voice}\n")

for voice in ca_available_voices:
    print(f"Testing voice: {voice}")
    create_mp3_file(text_ca, voice)
    print(f"Finished testing voice: {voice}\n")

for voice in eu_available_voices:
    print(f"Testing voice: {voice}")
    create_mp3_file(text_eu, voice)
    print(f"Finished testing voice: {voice}\n")

for voice in gl_available_voices:
    print(f"Testing voice: {voice}")
    create_mp3_file(text_gl, voice)
    print(f"Finished testing voice: {voice}\n")