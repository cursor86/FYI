from pydantic import BaseModel
from openai import OpenAI
import json


class MusicChoiceResponse(BaseModel):
    reasoning: str
    id: int


class OpenAIService:
    """
    Service to interact with the OpenAI API for generating video scripts, image prompts,
    and selecting appropriate background music.
    """

    def __init__(self, api_key: str):
        """
        Initialize the service with the provided API key.

        Args:
            api_key (str): OpenAI API key.
        """
        self.openai_client = OpenAI(api_key=api_key)

    def generate_script(self, theme: str, language: str) -> str:
        """
        Generate a humanized, conversational short video script.

        Args:
            theme (str): The subject of the script.
            language (str): The language in which the script is written.

        Returns:
            str: The generated script with natural speech elements.
        """
        prompt = (
            f"You are a skilled scriptwriter specialized in writing engaging, informal, and conversational scripts "
            f"for short videos (up to 60 seconds), such as YouTube Shorts, Reels, and TikTok. "
            f"Write a natural and authentic narration script about '{theme}' in {language}. "
            f"Include informal expressions, brief pauses (indicated by ellipses '...'), thoughtful interjections "
            f"('hmmm', 'you know'), casual laughter ('haha'), and other conversational elements to make the script "
            f"feel genuinely human and relatable. Do not include any scene directions or notes—only provide the narration text."
        )

        # Calls the Chat Completions endpoint
        completion = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        choice = completion.choices[0]
        return choice.message.content

    def generate_image_prompt(
        self, full_subtitles: str, previous_prompts: list, group_text: str
    ) -> str:
        """
        Generate a prompt for image generation based on subtitle context, 
        ensuring consistency of style across prompts, historical coherence if applicable, 
        and avoiding repetitive ideas.

        Args:
            full_subtitles (str): The entire subtitle text for context.
            previous_prompts (list): List of previously generated image prompts.
            group_text (str): The specific subtitle segment to create an image prompt for.

        Returns:
            str: The generated image prompt in English.
        """

        prompt = (
            "You are a creative prompt generator for text-to-image models. "
            "Your task is to maintain a consistent, coherent, and artistic style throughout all generated prompts, "
            "while ensuring each prompt remains fresh and distinctive. "
            "If the context implies a historical or thematic setting, incorporate accurate period elements to achieve authenticity. "
            "Avoid mentioning or including any text or lettering within the image itself. "
            "Do NOT generate or describe textual elements. "
            "Focus on visually capturing the essence of the scene described.\n\n"
            f"1. Subtitle context:\n{full_subtitles}\n\n"
        )

        if previous_prompts:
            prompt += (
                "2. Previously generated prompts (do not repeat these ideas; "
                "maintain overall style coherence while introducing new creative angles):\n"
                f"{previous_prompts}\n\n"
            )

        prompt += (
            f"3. Subtitle segment to visualize (without text):\n{group_text}\n\n"
            "Generate a single, concise, and artistically styled prompt in English, "
            "consistent with the established style but offering a novel perspective. "
            "Incorporate relevant historical or contextual details if applicable. "
            "Do not reference or encourage the inclusion of text or lettering. "
            "Present only one concise, final image prompt now."
        )

        completion = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        choice = completion.choices[0]
        return choice.message.content

    def generate_music_choice(
        self, script: str, image_prompts: list, songs_json: str
    ) -> MusicChoiceResponse:
        """
        Generate a background music choice based on the video script, image prompts, and available songs.

        Args:
            script (str): The video script.
            image_prompts (list): Generated image prompts for the video.
            songs_json (str): JSON representation of available songs.

        Returns:
            MusicChoiceResponse: Object containing the reasoning and the ID of the chosen song.
        """
        prompt = (
            "You are a creative assistant for selecting background music for videos. "
            "Based on the script below, the already generated image prompts, and the list of available songs, "
            "choose the music that best fits as background music for the video. "
            "The available songs list is provided in JSON format and contains objects with the keys 'id', 'file', 'keywords', 'artist', and 'source'.\n\n"
            f"Script:\n{script}\n\n"
            f"Image Prompts:\n{image_prompts}\n\n"
            f"Songs List (JSON):\n{songs_json}\n\n"
            "Respond ONLY with a valid JSON object following this schema:\n"
            '{ "reasoning": "(reason for choosing the music)", "id": (id of the chosen song) }'
        )

        # Force JSON response
        completion = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        choice = completion.choices[0]
        response_data = choice.message.content

        # Attempt to parse the response as JSON or dict
        if isinstance(response_data, dict):
            result_data = response_data
        elif isinstance(response_data, str):
            try:
                result_data = json.loads(response_data)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Could not decode JSON from the model response:\n{response_data}\n\nError: {e}"
                )
        elif hasattr(response_data, "to_dict"):
            result_data = response_data.to_dict()
        else:
            raise ValueError(
                f"Unexpected response type for message content: {type(response_data)}"
            )

        return MusicChoiceResponse(**result_data)

    def generate_script_and_voice_instructions(self, theme: str, language: str) -> dict:
        """
        Generates a JSON object containing the script and balanced humanized voice instructions.

        Args:
            theme (str): The theme for the script.
            language (str): The language for the script.

        Returns:
            dict: Object with the keys "script" and "voice_instructions".
        """
        prompt = (
            f"You are a creative scriptwriter specializing in engaging short video narrations "
            f"for short videos (up to 60 seconds), such as YouTube Shorts, Reels, and TikTok. "
            f"Write a natural, conversational narration script about '{theme}' in {language}. "
            f"Include realistic speech nuances sparingly and naturally, such as occasional short pauses (indicated by ellipses '...'), "
            f"thoughtful interjections ('hmmm...', 'well...', 'you know...'), or light laughter ('haha') only when truly appropriate. "
            f"Do NOT overuse pauses or expressions; keep them subtle and realistic, as in a genuine casual conversation. "
            f"Along with the script, provide detailed voice instructions under the key 'voice_instructions', specifying:\n"
            f"- 'accent_affect': brief description of accent nuances\n"
            f"- 'tone': overall mood (friendly, humorous, thoughtful, etc.)\n"
            f"- 'pacing': speech speed and rhythm (relaxed, dynamic, steady, etc.)\n"
            f"- 'emotion': primary emotional tone (enthusiastic, curious, playful, etc.)\n"
            f"- 'pronunciation': specific pronunciation notes if needed\n"
            f"- 'personality_affect': influence of personality on voice style\n\n"
            "Respond strictly as a JSON object without explanations or additional text. Example:\n"
            "{\n"
            '  "script": "Your balanced narration text here",\n'
            '  "voice_instructions": {\n'
            '    "accent_affect": "neutral American accent, conversational",\n'
            '    "tone": "friendly and informative",\n'
            '    "pacing": "steady with occasional natural pauses",\n'
            '    "emotion": "enthusiastic yet natural",\n'
            '    "pronunciation": "clear, standard pronunciation",\n'
            '    "personality_affect": "warm, approachable, genuine"\n'
            "  }\n"
            "}"
        )

        # Force JSON response
        completion = self.openai_client.chat.completions.create(
            model="gpt-4o",
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        choice = completion.choices[0]
        response_data = choice.message.content

        if isinstance(response_data, dict):
            result_data = response_data
        elif isinstance(response_data, str):
            try:
                result_data = json.loads(response_data)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Could not decode JSON from the model response:\n{response_data}\n\nError: {e}"
                )
        elif hasattr(response_data, "to_dict"):
            result_data = response_data.to_dict()
        else:
            raise ValueError(
                f"Unexpected response type for message content: {type(response_data)}"
            )

        return result_data
