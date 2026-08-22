import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a script and convert it to audio."
    )
    parser.add_argument("--theme", required=True,
                        help="The theme of the script.")
    parser.add_argument("--language", required=True,
                        help="The language of the script.")
    parser.add_argument("--tts_service", choices=["elevenlabs", "openai"], default="elevenlabs",
                        help="Choose which TTS service to use ('elevenlabs' or 'openai').")
    parser.add_argument("--voice_id",
                        help="The Eleven Labs voice ID to use.")
    parser.add_argument("--stability", type=float, default=0.75,
                        help="Stability setting for the voice (default: 0.75).")
    parser.add_argument("--similarity_boost", type=float, default=0.5,
                        help="Similarity boost setting for the voice (default: 0.5).")
    parser.add_argument("--max_duration", type=float, default=None,
                        help="Maximum duration for the audio in seconds. If the generated audio exceeds this duration, it will be accelerated to match it.")
    parser.add_argument("--openai_tts_model", default="tts-1-hd",
                        help="OpenAI TTS model name (default: tts-1-hd).")
    parser.add_argument("--openai_tts_voice", default="alloy",
                        help="OpenAI TTS voice name (default: alloy).")
    parser.add_argument("--watermark", type=str, default=None,
                        help="Optional watermark text to overlay on the video.")

    args = parser.parse_args()

    if args.tts_service == "elevenlabs" and not args.voice_id:
        parser.error(
            "--voice_id is required when --tts_service is 'elevenlabs'")

    return args
