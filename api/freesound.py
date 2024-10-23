from random import choice

from aiohttp import ClientSession
from loguru import logger

from config import freesound_oauth_token, freesound_api_token

base_url = "https://freesound.org/apiv2"


async def download_sound(sound_id: int):
    async with ClientSession() as session:
        oauth_headers = {"Authorization": f"Bearer {freesound_oauth_token}"}
        response = await session.get(f"{base_url}/sounds/{sound_id}/download", headers=oauth_headers)
        if response.status == 401:
            logger.error("OAUTH токен авторизации freesound недействителен, "
                         "обновите его при помощи скрипта freesound_oauth.py")
        return await response.read()


async def get_sound(query: str):
    headers = {"Authorization": f"Token {freesound_api_token}"}
    async with ClientSession() as session:
        response = await session.get(f"{base_url}/search/text/?query={query}", headers=headers)
        response.raise_for_status()
        json = await response.json()
        results = json["results"]
        if not results:
            raise ValueError("Не найдено аудиозаписей")
        sound = choice(results)
        sound_id = sound["id"]
        sound_name = sound["name"]
        return await download_sound(sound_id), sound_name
