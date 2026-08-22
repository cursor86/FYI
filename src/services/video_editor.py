from moviepy import (
    AudioFileClip,
    ImageClip,
    CompositeVideoClip,
    TextClip,
    CompositeAudioClip,
    concatenate_audioclips
)
from moviepy.video.fx import FadeIn, FadeOut, Resize
from moviepy.video.tools.subtitles import SubtitlesClip
import os
from utils.audio_processing import adjust_background_music_volume


def make_textclip(txt):
    """
    Creates a TextClip for subtitles.

    Args:
        txt (str): The subtitle text.

    Returns:
        TextClip: The formatted text clip.
    """
    return TextClip(
        text=txt,
        font="fonts/Helvetica.ttf",
        font_size=50,
        color="yellow",
        stroke_color="black",
        stroke_width=2,
        method="caption",
        size=(1000, None)
    )


def assemble_video(video_folder, file_id, cues, background_music_path=None, max_duration=None, watermark=None):
    """
    Assembles a final video by combining narration audio, images, subtitles, and optional background music.
    Optionally adds a textual watermark if 'watermark' is provided.

    Args:
        video_folder (str): The directory where video assets are stored.
        file_id (str): The unique identifier for the video.
        cues (list): Subtitle cues defining the timing of text overlays.
        background_music_path (str, optional): Path to the background music file. Defaults to None.
        max_duration (float, optional): The maximum allowed duration for the video.
        watermark (str, optional): Optional text to overlay as a watermark. Defaults to None.

    Returns:
        str: The path to the final video file.
    """

    # Load narration audio
    audio_path = os.path.join(video_folder, f"{file_id}.mp3")
    narration_audio = AudioFileClip(audio_path)
    video_duration = narration_audio.duration

    # Process background music if provided
    if background_music_path:
        adjusted_bg_music_path = adjust_background_music_volume(
            audio_path, background_music_path, target_diff=-15.0, output_dir=video_folder
        )

        bg_music = AudioFileClip(adjusted_bg_music_path)
        if bg_music.duration < video_duration:
            loops = int(video_duration // bg_music.duration) + 1
            bg_music = concatenate_audioclips([bg_music] * loops)
        if bg_music.duration > video_duration:
            bg_music = bg_music.with_duration(video_duration)
        combined_audio = CompositeAudioClip([narration_audio, bg_music])
    else:
        combined_audio = narration_audio

    # Create the base video with zoom effect on the first image
    first_image = os.path.join(video_folder, f"{file_id}_img_1.png")
    background = ImageClip(first_image).with_duration(video_duration)
    background = background.with_effects([Resize(lambda t: 1 + 0.02 * t)])

    # Add additional images with transitions
    image_clips = []
    num_images = (len(cues) + 1) // 2
    for i in range(1, num_images):
        group = cues[i * 2: i * 2 + 2]
        start = group[0][0]
        end = group[-1][1]
        duration = end - start

        img_path = os.path.join(video_folder, f"{file_id}_img_{i+1}.png")
        clip = ImageClip(img_path).with_duration(duration)
        clip = clip.with_start(start)
        clip = clip.with_effects([
            FadeIn(0.5),
            FadeOut(0.5),
            Resize(lambda t: 1 + 0.02 * t)
        ])
        image_clips.append(clip)

    # Create the video composition with images and transitions
    video = CompositeVideoClip([background] + image_clips, size=(1080, 1920))

    # Add subtitles
    srt_path = os.path.join(video_folder, f"{file_id}.srt")
    subtitles = SubtitlesClip(
        subtitles=srt_path, make_textclip=make_textclip
    ).with_position(("center", 1620))

    # Merge all elements together
    final = CompositeVideoClip([video, subtitles], size=(1080, 1920))
    final = final.with_audio(combined_audio)

    # If a watermark was provided, overlay it at the bottom-right
    if watermark:
        watermark_clip = (
            TextClip(
                text=watermark,
                font="fonts/Helvetica.ttf",
                font_size=48,
                color="white",
                stroke_color="black",
                stroke_width=1,
                method="label"
            )
            .with_duration(final.duration)
            .with_position(("center", "center"))
            .with_opacity(0.5)
        )
        final = CompositeVideoClip([final, watermark_clip], size=(1080, 1920))

    # Determine the final duration:
    # Get the end time of the last subtitle cue.
    if cues:
        last_subtitle_end = cues[-1][1]
    else:
        last_subtitle_end = video_duration

    # The desired duration is the maximum between the audio duration and
    # the last subtitle's end, but not exceeding max_duration (if provided).
    desired_duration = max(video_duration, last_subtitle_end)
    if max_duration is not None:
        desired_duration = min(desired_duration, max_duration)

    final = final.with_duration(desired_duration)

    # Export the final video
    output_path = os.path.join(video_folder, f"{file_id}_final.mp4")
    final.write_videofile(output_path, fps=24)

    return output_path
