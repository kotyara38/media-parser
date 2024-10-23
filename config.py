import os

from dotenv import load_dotenv

load_dotenv()

telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
unsplash_api_token = os.getenv('UNSPLASH_API_TOKEN')
freesound_client_id = os.getenv('FREESOUND_CLIENT_ID')
freesound_api_token = os.getenv('FREESOUND_API_TOKEN')
freesound_oauth_token = os.getenv('FREESOUND_OAUTH_TOKEN')
repository_url = "google.com"
