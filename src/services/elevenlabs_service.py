from elevenlabs import ElevenLabs, VoiceSettings
from io import BytesIO


class ElevenLabsService:
    """
    Service to interact with the Eleven Labs API for text-to-speech conversion.
    """

    def __init__(self, api_key):
        """
        Initialize the service with the API key.

        Args:
            api_key (str): Eleven Labs API key.
        """
        self.client = ElevenLabs(api_key=api_key)

    def text_to_speech(self, voice_id, text, stability=0.75, similarity_boost=0.85):
        """
        Convert text to speech using the specified voice and settings.

        Args:
            voice_id (str): ID of the voice to use.
            text (str): The text to convert.
            stability (float): Stability of the generated voice.
            similarity_boost (float): How much the voice matches the provided style.

        Returns:
            bytes: The raw audio data in MP3 format.
        """
        # Get the raw response from Eleven Labs as a stream of bytes
        response = self.client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost
            )
        )

        # Combine the streamed chunks into a single BytesIO object
        audio_data = BytesIO()
        for chunk in response:
            if chunk:
                audio_data.write(chunk)
        audio_data.seek(0)

        return audio_data.read()
