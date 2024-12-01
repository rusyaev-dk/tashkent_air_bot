from typing import Optional

from infrastructure.api.clients.http_client import HttpClient


class AQIClient:
    def __init__(self, http_client: HttpClient, base_url: str, token: str):
        """
        Initializes the API repositories implementation.

        :param http_client: The HTTP client instance for making requests.
        :param base_url: The base URL of the API.
        :param token: The API token for authentication.
        """
        self.http_client = http_client
        self.base_url = base_url
        self.token = token

    async def request_aqi(self, lat: float, lon: float) -> Optional[dict]:
        """
        Fetches AQI data for the specified latitude and longitude.

        :param lat: Latitude of the location.
        :param lon: Longitude of the location.
        :return: AQI data in JSON format.
        """
        endpoint = "data/2.5/air_pollution"
        url = f"{self.base_url}/{endpoint}"
        # headers = {"Authorization": f"Bearer {self.token}"}
        params = {"lat": lat, "lon": lon, "appid": self.token}

        return await self.http_client.make_request(url, params=params)
