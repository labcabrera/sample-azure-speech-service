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

key = os.environ.get('SPEECH_KEY')
region = os.environ.get('SPEECH_REGION')

if not key or not region:
    raise ValueError("Please set the SPEECH_KEY and SPEECH_REGION environment variables.")

text_es = "El número de teléfono de la oficina Avenida de las Pruebas es seis cinco cinco, cuatro dos, tres uno, uno cuatro. Se lo repito. Seis cinco cinco, cuatro dos, tres uno, uno cuatro."
text_ca = "El número de telèfon de l'oficina Avinguda de les Proves és sis cinc cinc, quatre dos, tres un, un quatre. Li ho repeteixo. Sis cinc cinc, quatre dos, tres un, un quatre."
text_eu = "Avenida de las Pruebas bulegoko telefono zenbakia sei bost bost, lau bi, hiru bat, bat lau da. Errepikatuko dut. Sei bost bost, lau bi, hiru bat, bat lau."
text_gl = "O número de teléfono da oficina da Avenida de las Pruebas é seis cinco cinco, catro dous, tres un, un catro. Repetireino. Seis cinco cinco, catro dous, tres un, un catro."

speech_config = speechsdk.SpeechConfig(subscription=key, endpoint=region)

def create_mp3_file(text: str, voice: str):
    start_time = time.time()
    
    audio_config = speechsdk.audio.AudioOutputConfig(filename="output/output-{}.mp3".format(voice))
    speech_config.speech_synthesis_voice_name=voice
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    end_time = time.time()
    execution_time = end_time - start_time

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}] and saved to output-{}.mp3".format(text, voice))
        print("Execution time: {:.2f} seconds".format(execution_time))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        print("Execution time: {:.2f} seconds".format(execution_time))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and endpoint values?")

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