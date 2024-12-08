import aiohttp


class HttpClient:
    def __init__(self):
        """
        Initializing an HTTP client with an aiohttp session.
        """
        self.__session = aiohttp.ClientSession()

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
