from aiohttp import ClientSession

from config import unsplash_api_token


async def get_random_image(query: str):
    headers = {"Authorization": f"Client-ID {unsplash_api_token}",
               "Accept-Version": "v1"}
    parameters = {"query": query}
    async with ClientSession() as session:
        response = await session.get("https://api.unsplash.com/photos/random", headers=headers, params=parameters)
        response.raise_for_status()
        json = await response.json()
        image_url = json["urls"]["full"]
        image_id = json["id"]
        return image_url, image_id
