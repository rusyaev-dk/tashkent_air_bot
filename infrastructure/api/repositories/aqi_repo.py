import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import insert, select, delete

from infrastructure.api.aqi_converter import AqiConverter
from infrastructure.api.exceptions import ApiException
from infrastructure.api.models.models import AQI
from infrastructure.api.clients.aqi_client import AQIClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.aqi import AQILocal
from tgbot.services import generate_random_id


class AQIRepository:
    def __init__(self, aqi_client: AQIClient, session: AsyncSession):
        self.__client = aqi_client
        self.__session = session
        self.__default_lat = 41.2646
        self.__default_lon = 69.2163

    async def get_aqi(self) -> Optional[AQI]:
        stmt = select(AQILocal).order_by(AQILocal.created_at.desc()).limit(1)
        local = await self.__session.scalar(stmt)

        if not local:
            return None
        return AQI.from_local(local)

    async def update_aqi(self, lat: float = None, lon: float = None) -> None:
        lat = self.__default_lat if not lat else lat
        lon = self.__default_lon if not lon else lon

        response = await self.__request_aqi(lat, lon)
        if not response:
            return

        pollutants = response["list"][0]["components"]
        aqi_usa: int = AqiConverter.convert_to_usa_aqi(pollutants)[0]  # returns tuple with detailed dict

        request_id = generate_random_id(length=15)
        timestamp = response["list"][0]["dt"]

        date = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        stmt = delete(AQILocal)
        await self.__session.execute(stmt)

        stmt = insert(AQILocal).values(
            request_id=request_id,
            aqi=aqi_usa,
            pm25=pollutants.get("pm2_5", 0.0),
            pm10=pollutants.get("pm10", 0.0),
            o3=pollutants.get("o3", 0.0),
            lat=lat,
            lon=lon,
            date=date
        ).prefix_with("OR REPLACE")
        await self.__session.execute(stmt)

        await self.__session.commit()

    async def __request_aqi(self, lat: float, lon: float) -> Optional[dict]:
        try:
            response = await self.__client.get_aqi(lat, lon)
            return response
        except ApiException as exception:
            logging.error(exception.what())
            return None
        except KeyError as exception:
            logging.error(exception)
            return None
