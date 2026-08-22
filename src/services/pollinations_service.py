import urllib.request
import urllib.parse


class PollinationsService:
    """
    Service to interact with the free Pollinations.ai image generation API.
    """

    def generate_image(self, prompt: str, output_path: str, width: int = 1080, height: int = 1920) -> None:
        """
        Generate an image from a text prompt and save it to disk.

        Args:
            prompt (str): The text prompt describing the desired image.
            output_path (str): Path where the generated image will be saved.
            width (int): Output image width in pixels (default: 1080).
            height (int): Output image height in pixels (default: 1920).
        """
        encoded_prompt = urllib.parse.quote(prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}&nologo=true"
        )

        urllib.request.urlretrieve(url, output_path)
