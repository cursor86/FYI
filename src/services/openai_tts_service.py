from openai import OpenAI
import tempfile
import os


class OpenAITTSService:
    """
    Service to interact with the OpenAI API for text-to-speech conversion.
    """

    def __init__(self, api_key):
        """
        Initialize the service with the API key.

        Args:
            api_key (str): OpenAI API key.
        """
        self.client = OpenAI(api_key=api_key)

    def text_to_speech(self, text, model="gpt-4o-mini-tts", voice="ash", instructions=None):
        """
        Converts text to speech using the specified model and voice.

        Args:
            text (str): The text to be converted.
            model (str): The TTS model to be used (default: "gpt-4o-mini-tts").
            voice (str): The voice to be used (default: "ash").
            instructions (str, optional): Additional instructions to define voice characteristics.

        Returns:
            bytes: The generated speech audio data in MP3 format.
        """
        params = {
            "model": model,
            "voice": voice,
            "input": text,
        }
        if instructions:
            params["instructions"] = instructions

        response = self.client.audio.speech.create(**params)

        # Create a temporary file to store the generated speech
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_file_path = tmp_file.name

        response.stream_to_file(tmp_file_path)

        try:
            with open(tmp_file_path, "rb") as f:
                audio_data = f.read()
        finally:
            os.remove(tmp_file_path)

        return audio_data
