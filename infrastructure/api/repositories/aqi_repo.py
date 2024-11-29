import logging

from typing import Optional

from sqlalchemy import insert, select, delete

from infrastructure.api.exceptions import ApiException
from infrastructure.api.models.models import AQI
from infrastructure.api.clients.aqi_client import AQIClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.aqi import AQILocal


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

        local = AQILocal.from_json(json=response)
        await self.__rewrite_aqi(local=local)

    async def __rewrite_aqi(self, local: AQILocal):
        stmt = delete(AQILocal)
        await self.__session.execute(stmt)

        stmt = insert(AQILocal).values(local.__dict__).prefix_with("OR REPLACE")
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
