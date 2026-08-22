from openai import OpenAI


class WhisperService:
    """
    Service to interact with OpenAI's Whisper API for audio transcription.
    """

    def __init__(self, api_key: str):
        """
        Initialize the service with the API key.
        """
        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_file_path: str):
        """
        Transcribe the provided audio file into a verbose JSON format with word-level timestamps.
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    # request word-level timestamps
                    timestamp_granularities=["word"]
                )
            return transcription
        except Exception as e:
            raise RuntimeError(f"Error transcribing audio: {e}")
