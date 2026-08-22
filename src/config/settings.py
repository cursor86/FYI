import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
SANA_MODEL_VERSION = os.getenv(
    'SANA_MODEL_VERSION', 'c6b5d2b7459910fec94432e9e1203c3cdce92d6db20f7145747990b52fa6')

if not OPENAI_API_KEY:
    raise ValueError(
        "The OPENAI_API_KEY variable was not found in the .env file."
    )

if not ELEVENLABS_API_KEY:
    raise ValueError(
        "The ELEVENLABS_API_KEY variable was not found in the .env file."
    )

if not REPLICATE_API_TOKEN:
    raise ValueError(
        "The REPLICATE_API_TOKEN variable was not found in the .env file."
    )
