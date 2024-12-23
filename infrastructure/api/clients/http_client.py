import ssl

import aiohttp
import certifi
from aiohttp import TCPConnector


class HttpClient:
    def __init__(self):
        """
        Initializing an HTTP client with an aiohttp session.
        """

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = TCPConnector(ssl=ssl_context)
        self.__session = aiohttp.ClientSession(connector=connector)

    async def make_request(
            self,
            url: str,
            method: str = "GET",
            headers: dict = None,
            params: dict = None
    ) -> dict:
        async with self.__session.request(method, url, headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def close(self):
        await self.__session.close()
