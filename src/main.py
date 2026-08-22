import sys
import os
import uuid
import logging
from config import settings
from parsers.arguments import parse_args
from services.openai_service import OpenAIService
from services.elevenlabs_service import ElevenLabsService
from services.whisper_service import WhisperService
from services.openai_tts_service import OpenAITTSService
from services.replicate_service import ReplicateService
from utils.file_handler import save_audio, save_subtitles, save_image
from utils.logger import setup_logger
from utils.audio_processing import reprocess_audio
from utils.subtitle_handler import align_words_with_punctuation, format_srt_from_aligned_words


def main():
    """
    Main entry point for the application.
    - Generates a script using OpenAI API.
    - Converts the script to speech using Eleven Labs or OpenAI TTS API.
    - Processes the audio if max_duration is specified.
    - Generates subtitles from the audio using OpenAI's Whisper API.
    - Generates images based on subtitle intervals using the Replicate API.
    - Assembles the final video using the generated audio, images, subtitles, and animated transitions.
    All outputs (audio, subtitles, images, and log file) are saved in a dedicated folder for each video.
    """
    logger = setup_logger()
    args = parse_args()

    # Initialize services
    logger.info("Initializing services...")
    openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)
    elevenlabs_service = ElevenLabsService(api_key=settings.ELEVENLABS_API_KEY)
    whisper_service = WhisperService(api_key=settings.OPENAI_API_KEY)

    # Generate script (and voice instructions if using OpenAI TTS)
    if args.tts_service == "elevenlabs":
        logger.info("Generating script with OpenAI...")
        try:
            script_text = openai_service.generate_script(
                theme=args.theme, language=args.language
            )
            logger.debug(f"Generated script: {script_text}")
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            sys.exit(1)
    else:
        logger.info(
            "Generating script and voice instructions with OpenAI TTS...")
        try:
            result = openai_service.generate_script_and_voice_instructions(
                theme=args.theme, language=args.language
            )
            script_text = result.get("script")
            voice_instructions_obj = result.get("voice_instructions")
            instructions_str = (
                f"Accent/Affect: {voice_instructions_obj.get('accent_affect')}; "
                f"Tone: {voice_instructions_obj.get('tone')}; "
                f"Pacing: {voice_instructions_obj.get('pacing')}; "
                f"Emotion: {voice_instructions_obj.get('emotion')}; "
                f"Pronunciation: {voice_instructions_obj.get('pronunciation')}; "
                f"Personality Affect: {voice_instructions_obj.get('personality_affect')}"
            )
            logger.debug(f"Generated script: {script_text}")
            logger.debug(f"Generated voice instructions: {instructions_str}")
        except Exception as e:
            logger.error(
                f"Error generating script and voice instructions: {e}")
            sys.exit(1)

    # Choose TTS service and convert script to audio
    try:
        if args.tts_service == "elevenlabs":
            logger.info("Converting text to speech with Eleven Labs...")
            response = elevenlabs_service.text_to_speech(
                voice_id=args.voice_id,
                text=script_text,
                stability=args.stability,
                similarity_boost=args.similarity_boost
            )
        else:
            logger.info("Converting text to speech with OpenAI TTS...")
            tts_service = OpenAITTSService(api_key=settings.OPENAI_API_KEY)
            response = tts_service.text_to_speech(
                text=script_text,
                model=args.openai_tts_model,
                voice=args.openai_tts_voice,
                instructions=instructions_str
            )

        # Generate a unique file_id for this video and create a dedicated output folder
        file_id = str(uuid.uuid4())
        video_folder = f"output/{file_id}"
        if not os.path.exists(video_folder):
            os.makedirs(video_folder)

        # Add a file handler to the logger to save logs in the video folder
        file_handler = logging.FileHandler(
            f"{video_folder}/process.log", mode='w', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

        output_file = save_audio(
            response, directory=video_folder, file_id=file_id)
        logger.info(
            f"Audio successfully generated and saved as {output_file}.")
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        sys.exit(1)

    # Process audio if max_duration is provided
    if args.max_duration:
        logger.info(
            f"Processing audio to ensure it does not exceed {args.max_duration} seconds...")
        try:
            with open(output_file, 'rb') as f:
                audio_bytes = f.read()

            processed_bytes = reprocess_audio(
                audio_data=audio_bytes,
                max_duration=args.max_duration,
                logger=logger
            )

            if processed_bytes != audio_bytes:
                with open(output_file, 'wb') as f:
                    f.write(processed_bytes)
                logger.info(
                    f"Audio processed successfully and saved as {output_file}.")
                logger.debug(
                    f"Original audio file {output_file} overwritten after processing.")
            else:
                logger.info(
                    "Audio duration is within the maximum duration. No processing needed.")

        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            sys.exit(1)

    # Generate subtitles from audio
    logger.info("Generating subtitles with Whisper...")
    try:
        transcript = whisper_service.transcribe_audio(
            audio_file_path=output_file)

        logger.info("Timing data of all words returned by Whisper:")
        for word in transcript.words:
            logger.info("Word: '%s', start: %s, end: %s",
                        word.word, word.start, word.end)

        aligned_words = align_words_with_punctuation(
            transcript.words, transcript.text)
        srt_content, cues = format_srt_from_aligned_words(aligned_words)
        subtitle_file = save_subtitles(
            srt_content, directory=video_folder, file_id=file_id)
        logger.info(f"Subtitles generated and saved as {subtitle_file}.")
    except Exception as e:
        logger.error(f"Error generating subtitles: {e}")
        sys.exit(1)

    # Generate images based on subtitle intervals
    logger.info(
        "Generating images based on subtitle intervals using Replicate...")
    try:
        replicate_service = ReplicateService(
            api_token=settings.REPLICATE_API_TOKEN)
        # Initialize list to store prompts generated for images in this video
        previous_image_prompts = []
        # Group cues in pairs (each image will cover up to two subtitle intervals)
        for i in range(0, len(cues), 2):
            group = cues[i:i+2]
            group_text = " ".join([cue[2] for cue in group])
            # Generate the image prompt using the language model with the required context and instructions
            image_prompt = openai_service.generate_image_prompt(
                full_subtitles=srt_content,
                previous_prompts=previous_image_prompts,
                group_text=group_text
            )
            # Log the generated image prompt
            logger.info(f"Image prompt for cue {(i // 2) + 1}: {image_prompt}")
            previous_image_prompts.append(image_prompt)
            image_data = replicate_service.generate_image(
                image_prompt, width=1080, height=1920)
            image_file = save_image(
                image_data,
                directory=video_folder,
                file_id=file_id,
                suffix=f"img_{(i // 2) + 1}"
            )
            logger.info(f"Image generated and saved as {image_file}.")
    except Exception as e:
        logger.error(f"Error generating images: {e}")
        sys.exit(1)

    # Select background music based on script, image prompts, and available songs
    logger.info("Selecting background music using OpenAI...")
    try:
        import json
        # Load songs data from songs/songs.json
        with open("songs/songs.json", "r", encoding="utf-8") as f:
            songs_data = json.load(f)
        # Convert songs_data to formatted JSON string
        songs_json = json.dumps(songs_data, ensure_ascii=False, indent=2)
        # Generate music choice using the language model
        music_choice_response = openai_service.generate_music_choice(
            script=script_text,
            image_prompts=previous_image_prompts,
            songs_json=songs_json
        )
        # Parse the response JSON
        music_choice = music_choice_response.dict()
        logger.info(f"Background music selected: {music_choice}")
        # Find the chosen song in songs_data
        chosen_song = next(
            (song for song in songs_data if song["id"] == music_choice["id"]), None)
        if not chosen_song:
            logger.error("Invalid song ID returned by music selection.")
            sys.exit(1)
        # Construct the path to the music file in songs/mp3 folder
        background_music_path = os.path.join(
            "songs", "mp3", chosen_song["file"])
    except Exception as e:
        logger.error(f"Error selecting background music: {e}")
        sys.exit(1)

    # Assemble the final video using audio, images, subtitles, and transitions
    logger.info(
        "Assembling final video with audio, images, subtitles, and transitions...")
    try:
        from services.video_editor import assemble_video
        final_video_path = assemble_video(
            video_folder=video_folder,
            file_id=file_id,
            cues=cues,
            background_music_path=background_music_path,
            max_duration=args.max_duration,
            watermark=args.watermark
        )
        logger.info(f"Final video assembled and saved as {final_video_path}.")
    except Exception as e:
        logger.error(f"Error assembling final video: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
