import os
import uuid


def save_audio(response, directory="output", file_id=None):
    """
    Saves audio data to a file.

    :param response: The audio data to save (bytes).
    :param directory: The directory where the audio file will be saved.
    :param file_id: An optional unique identifier to name the file.
    :return: Path to the saved audio file.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not file_id:
        file_id = str(uuid.uuid4())

    output_file = f"{directory}/{file_id}.mp3"

    with open(output_file, "wb") as f:
        f.write(response)

    return output_file


def save_subtitles(srt_content, directory="output", file_id=None):
    """
    Saves subtitle data to an SRT file.

    :param srt_content: The subtitle content.
    :param directory: The directory where the SRT file will be saved.
    :param file_id: An optional unique identifier to name the file.
    :return: Path to the saved SRT file.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not file_id:
        file_id = str(uuid.uuid4())

    subtitle_file = f"{directory}/{file_id}.srt"

    with open(subtitle_file, "w", encoding="utf-8") as f:
        f.write(srt_content)

    return subtitle_file


def save_image(image_data, directory="output", file_id=None, suffix="image", watermark=None):
    """
    Saves image bytes to a PNG file and optionally applies a watermark.

    :param image_data: Image data (bytes).
    :param directory: Directory where the image will be saved.
    :param file_id: Optional custom identifier for the file name.
    :param suffix: Suffix to append to the filename (before the extension).
    :return: Path to the saved image file.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not file_id:
        file_id = str(uuid.uuid4())

    output_file = f"{directory}/{file_id}_{suffix}.png"

    # Save raw image data
    with open(output_file, "wb") as f:
        f.write(image_data)

    return output_file
