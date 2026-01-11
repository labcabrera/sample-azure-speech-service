import os
import azure.cognitiveservices.speech as speechsdk

key = os.environ.get('SPEECH_KEY')
region = os.environ.get('SPEECH_ENDPOINT')

speech_config = speechsdk.SpeechConfig(subscription=key, endpoint=region)

def get_available_voices_for_language(language_code: str):
    try:
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        voices_result = synthesizer.get_voices_async().get()
        if voices_result.reason == speechsdk.ResultReason.VoicesListRetrieved:
            filtered_voices = []
            for voice in voices_result.voices:
                if voice.locale.startswith(language_code):
                    filtered_voices.append({
                        'name': voice.name,
                        'locale': voice.locale,
                        'gender': voice.gender.name,
                        'voice_type': voice.voice_type.name
                    })            
            print(f"Available voices for language '{language_code}':")
            for voice in filtered_voices:
                print(f"  - {voice['name']} ({voice['locale']}) - {voice['gender']} - {voice['voice_type']}")
            
            return filtered_voices
        else:
            print(f"Error retrieving voices: {voices_result.reason}")
            return []
            
    except Exception as e:
        print(f"Error retrieving voices: {e}")
        return []

print("=" * 50)
print("GETTING AVAILABLE VOICES FROM AZURE")
print("=" * 50)

spanish_voices = get_available_voices_for_language('es')
print("\n")
catalan_voices = get_available_voices_for_language('ca')
print("\n")
euskera_voices = get_available_voices_for_language('eu')
print("\n")
galician_voices = get_available_voices_for_language('gl')
