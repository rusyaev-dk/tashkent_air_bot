import asyncio
import traceback
from typing import List, Dict, Any

from infrastructure.api.base import BaseClient
from infrastructure.api.exceptions import ApiResponseCodeException


class AQIClient(BaseClient):
    def __init__(self, api_key: str, **kwargs):
        self.__api_key = api_key
        self.__base_url = "https://api.waqi.info"
        super().__init__(base_url=self.__base_url)

    async def get_aqi_response(self, station_id: str) -> Dict[str, Any]:
        params = {
            "token": self.__api_key
        }

        url = f"/feed/{station_id}/"
        response = await self._make_request(url=url, method="GET", params=params)

        if response[0] != 200:
            raise ApiResponseCodeException(response_code=response[0], traceback=traceback.format_exc())
        return response[1]
