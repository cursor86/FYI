from pydub import AudioSegment
from io import BytesIO
import os


def reprocess_audio(audio_data: bytes,
                    max_duration: float = None,
                    speedup_chunk: int = 150,
                    speedup_crossfade: int = 25,
                    target_bitrate: str = "320k",
                    logger=None) -> bytes:
    """
    Reprocess the audio to optionally adjust duration and export with a specified bitrate.

    Args:
        audio_data (bytes): The original audio data in bytes format.
        max_duration (float, optional): Maximum allowed duration in seconds. If provided and
                                        the audio exceeds this duration, it will be sped up.
        speedup_chunk (int): Chunk size parameter for the speedup function.
        speedup_crossfade (int): Crossfade parameter for smoothing transitions in speedup.
        target_bitrate (str): Desired MP3 bitrate (e.g., "320k" for higher quality).
        logger: Logger instance for logging.

    Returns:
        bytes: The processed audio data in MP3 format.
    """
    # Load the audio from the byte stream
    audio = AudioSegment.from_file(BytesIO(audio_data), format="mp3")

    # If max_duration is defined, check the duration and speed up if necessary
    if max_duration is not None:
        # Convert milliseconds to seconds
        current_duration = len(audio) / 1000.0
        if current_duration > max_duration:
            speed_factor = current_duration / max_duration
            if logger:
                logger.info(f"Current duration {current_duration} exceeds max duration {max_duration}. "
                            f"Speeding up by a factor of {speed_factor}.")
            # Adjust playback speed with chunking and crossfade for smoother transitions
            audio = audio.speedup(
                playback_speed=speed_factor,
                chunk_size=speedup_chunk,
                crossfade=speedup_crossfade
            )
        else:
            # If no processing is needed, return the original data
            return audio_data

    # Re-export the audio with the specified bitrate
    output_data = BytesIO()
    audio.export(output_data, format="mp3",
                 parameters=["-b:a", target_bitrate])
    output_data.seek(0)

    return output_data.read()


def adjust_background_music_volume(narration_path: str, bg_music_path: str, target_diff: float = -10.0, output_dir: str = None) -> str:
    """
    Adjusts the volume of the background music so that it is target_diff dB quieter than the narration.

    Args:
        narration_path (str): Path to the narration audio file (MP3).
        bg_music_path (str): Path to the background music file (MP3).
        target_diff (float): Desired difference in dBFS (default: -10.0 dB, meaning background is 10 dB quieter than narration).
        output_dir (str, optional): Directory to save the adjusted background music file. If not provided, uses the directory of bg_music_path.

    Returns:
        str: Path to the adjusted background music audio file (temporary).
    """
    narration_audio = AudioSegment.from_file(narration_path, format="mp3")
    bg_music = AudioSegment.from_file(bg_music_path, format="mp3")

    narration_dbfs = narration_audio.dBFS
    bg_music_dbfs = bg_music.dBFS
    current_diff = bg_music_dbfs - narration_dbfs
    gain_adjustment = target_diff - current_diff
    adjusted_bg_music = bg_music.apply_gain(gain_adjustment)

    # Use output_dir if provided; otherwise, use the directory of bg_music_path
    if output_dir is None:
        output_dir = os.path.dirname(bg_music_path)

    temp_path = os.path.join(output_dir, "adjusted_bg_music.mp3")
    adjusted_bg_music.export(temp_path, format="mp3")
    return temp_path
