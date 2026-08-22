import edge_tts


class EdgeTTSService:
    """
    Service to interact with the free Microsoft Edge text-to-speech engine.
    """

    def __init__(self, voice: str = "en-US-ChristopherNeural"):
        """
        Initialize the service with the voice to use.

        Args:
            voice (str): The Edge TTS voice name (default: "en-US-ChristopherNeural").
        """
        self.voice = voice

    async def generate_voiceover(self, text: str, output_audio_path: str) -> None:
        """
        Convert text to speech and save it to disk.

        Args:
            text (str): The text to be converted.
            output_audio_path (str): Path where the generated audio will be saved.
        """
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_audio_path)
