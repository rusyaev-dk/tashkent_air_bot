import logging
from typing import Optional

from infrastructure.api.clients.http_client import HttpClient


class AQIClient:
    def __init__(
            self,
            http_client: HttpClient,
            aqicn_base_url: str,
            aqicn_token: str,
            owm_base_url: str,
            owm_token: str
    ):
        """
        Initializes the AQICN API client with fallback to OpenWeatherMap.

        :param http_client: The HTTP client for making requests.
        :param aqicn_base_url: The base URL of the AQICN API.
        :param aqicn_token: The AQICN API token for authentication.
        :param owm_base_url: The base URL of the OpenWeatherMap API.
        :param owm_token: The OpenWeatherMap API token for authentication.
        """
        self.http_client = http_client
        self.aqicn_base_url = aqicn_base_url.rstrip("/")
        self.aqicn_token = aqicn_token
        self.owm_base_url = owm_base_url.rstrip("/")
        self.owm_token = owm_token

    async def request_aqicn_data(self, station_id: str) -> Optional[dict]:
        """
        Fetch AQI data from AQICN for a specific station ID.

        :param station_id: The station ID.
        :return: AQI data in JSON format, or None if the request fails.
        """
        endpoint = f"feed/{station_id}/"
        url = f"{self.aqicn_base_url}/{endpoint}"
        params = {"token": self.aqicn_token}
        try:
            data = await self.http_client.make_request(url, params=params)
            if data and data.get("status") == "ok":
                return data.get("data")
        except Exception as e:
            logging.error(f"AQICN request failed for station {station_id}. Error: {e}")
        return None

    async def request_owm_data(self, lat: float, lon: float) -> Optional[dict]:
        """
        Fetch AQI data from OpenWeatherMap for specific coordinates.

        :param lat: Latitude of the location.
        :param lon: Longitude of the location.
        :return: AQI data in JSON format, or None if the request fails.
        """
        endpoint = "data/2.5/air_pollution"
        url = f"{self.owm_base_url}/{endpoint}"
        params = {"lat": lat, "lon": lon, "appid": self.owm_token}

        try:
            data = await self.http_client.make_request(url, params=params)
            return data
        except Exception as e:
            logging.error(f"OpenWeatherMap request failed: {e}")
            return None
