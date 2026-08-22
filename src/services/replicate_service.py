import replicate
from io import BytesIO
from config import settings


class ReplicateService:
    """
    Service to interact with the Replicate API for image generation using the nvidia/sana model.
    """

    def __init__(self, api_token):
        """
        Initialize the service with the Replicate API token.

        Args:
            api_token (str): Replicate API token.
        """
        self.api_token = api_token

    def generate_image(self, prompt, width=1080, height=1920):
        """
        Generate an image based on the given prompt using the nvidia/sana model.

        Args:
            prompt (str): The prompt describing the image to generate.
            width (int): The width of the generated image.
            height (int): The height of the generated image.

        Returns:
            bytes: The generated image data.
        """
        input_data = {
            "prompt": prompt,
            "width": width,
            "height": height
        }
        model_id = f"nvidia/sana:{settings.SANA_MODEL_VERSION}"
        output = replicate.run(
            model_id,
            input=input_data
        )
        try:
            return output.read()
        except AttributeError:
            return output
