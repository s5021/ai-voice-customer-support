from deepgram import DeepgramClient, SpeakOptions, PrerecordedOptions, FileSource
import base64
class DeepgramService:
    def __init__(self, api_key):
        self.client = DeepgramClient(api_key)
    def transcribe_audio(self, audio_data):
        try:
            if isinstance(audio_data, str):
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                language="en-US",
            )
            payload = {
                "buffer": audio_bytes,
            }
            response = self.client.listen.prerecorded.v("1").transcribe_file(
                payload, options
            )
            transcript = response.results.channels[0].alternatives[0].transcript
            return transcript
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None
    def synthesize_speech(self, text):
        try:
            options = SpeakOptions(
                model="aura-asteria-en",
                encoding="linear16",
                sample_rate=24000
            )
            response = self.client.speak.v("1").save(
                "output.wav",
                {"text": text},
                options
            )
            with open("output.wav", "rb") as audio_file:
                audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            return audio_base64
        except Exception as e:
            print(f"Error synthesizing speech: {e}")
            return None
