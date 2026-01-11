import os
from typing import Optional

import azure.cognitiveservices.speech as speechsdk


def _get_speech_config() -> speechsdk.SpeechConfig:
    key = os.environ.get('SPEECH_KEY')
    region_or_endpoint = os.environ.get('SPEECH_REGION') or os.environ.get('SPEECH_ENDPOINT')

    if not key or not region_or_endpoint:
        raise ValueError("Please set SPEECH_KEY and SPEECH_REGION (or SPEECH_ENDPOINT) environment variables.")

    if region_or_endpoint.startswith('http'):
        return speechsdk.SpeechConfig(subscription=key, endpoint=region_or_endpoint)
    else:
        return speechsdk.SpeechConfig(subscription=key, region=region_or_endpoint)


def transcribe_wav(file_path: str) -> Optional[str]:
    """Transcribe a single WAV file using Azure Speech SDK. Returns the recognized text or None."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    speech_config = _get_speech_config()
    # speech_config.speech_recognition_language = "es-ES"
    audio_input = speechsdk.audio.AudioConfig(filename=file_path)

    #  Si conocemos el idioma de antemano, usar esta línea:
    # recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    # Si no conocemos el idioma de antemano, usar la detección automática de idioma:
    adc = speechsdk.AutoDetectSourceLanguageConfig(languages=["es-ES","ca-ES"])
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input, auto_detect_source_language_config=adc)

    result = recognizer.recognize_once_async().get()

    # Debug output to help diagnose why no transcription was returned
    print(f"[DEBUG] result.reason = {result.reason}")
    print(f"[DEBUG] result.text = {getattr(result, 'text', None)}")
    if hasattr(result, 'cancellation_details') and result.cancellation_details is not None:
        cd = result.cancellation_details
        print(f"[DEBUG] cancellation.reason = {cd.reason}")
        print(f"[DEBUG] cancellation.error_details = {getattr(cd, 'error_details', None)}")
    if hasattr(result, 'no_match_details') and getattr(result, 'no_match_details', None) is not None:
        nm = result.no_match_details
        print(f"[DEBUG] no_match_details = {nm}")

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized from the audio (NoMatch).")
        return None
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        print(f"Recognition canceled: {details.reason}")
        if details.reason == speechsdk.CancellationReason.Error:
            if details.error_details:
                print(f"Error details: {details.error_details}")
                print("Check SPEECH_KEY and SPEECH_REGION (or SPEECH_ENDPOINT).")
        return None
    else:
        return None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Transcribe a WAV file using Azure Speech.')
    parser.add_argument('file', nargs='?', default='output/output-es-ES-ElviraNeural.mp3', help='Path to WAV file to transcribe')
    args = parser.parse_args()

    try:
        text = transcribe_wav(args.file)
        if text:
            print('Transcription result:')
            print(text)
        else:
            print('No transcription returned.')
    except Exception as e:
        print(f'Error: {e}')
