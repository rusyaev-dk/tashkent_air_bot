import aiohttp


class HttpClient:
    def __init__(self):
        """
        Инициализация HTTP клиента с сессией aiohttp.
        """
        self.session = aiohttp.ClientSession()

    async def make_request(self, url: str, method: str = "GET", headers: dict = None, params: dict = None) -> dict:
        """
        Выполняет HTTP-запрос.
        :param url: Полный URL запроса.
        :param method: HTTP метод (GET, POST и т. д.).
        :param headers: Заголовки запроса.
        :param params: Параметры запроса.
        :return: Ответ в формате JSON.
        """
        async with self.session.request(method, url, headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def close(self):
        """
        Закрывает HTTP-сессию.
        """
        await self.session.close()

    # def __del__(self):
    #     self.session.close()
    #     print('session closed')
