from datetime import datetime

from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from infrastructure.api.models.aqi import AQI
from infrastructure.api.clients.aqi_client import AQIClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.aqi import AQILocal


class AQIRepository:
    def __init__(self, aqi_client: AQIClient, session: AsyncSession):
        self.__client = aqi_client
        self.__session = session
        self.__default_lat = 41.2646
        self.__default_lon = 69.2163

    async def add_aqi(
            self,
            request_id: str,
            aqi: int,
            pm25: float,
            pm10: float,
            o3: float,
            lat: float,
            lon: float,
            date: datetime
    ) -> AQILocal:
        stmt = (
            insert(AQILocal)
            .values(
                request_id=request_id,
                aqi=aqi,
                pm25=pm25,
                pm10=pm10,
                o3=o3,
                lat=lat,
                lon=lon,
                date=date
            ).on_conflict_do_update(
                index_elements=[AQILocal.request_id],
                set_={
                    "date": date,
                    "pm25": pm25,
                    "pm10": pm10,
                    "o3": o3
                }
            ).returning(AQILocal)
        )
        result = await self.__session.execute(stmt)
        await self.__session.commit()

        return result.scalar_one()

    async def get_aqi(self) -> Optional[AQI]:
        stmt = select(AQILocal).order_by(AQILocal.created_at.desc()).limit(1)
        local = await self.__session.scalar(stmt)

        if not local:
            return None
        return AQI.from_local(local)

    async def update_aqi(self, lat: float = None, lon: float = None) -> None:
        lat = self.__default_lat if not lat else lat
        lon = self.__default_lon if not lon else lon

        json = await self.__client.request_aqi(lat, lon)
        if not json:
            return

        local = AQILocal.from_json(json)
        if await self.get_aqi():
            stmt = update(AQILocal).values(
                aqi=local.aqi,
                pm25=local.pm25,
                pm10=local.pm10,
                o3=local.o3,
                lat=local.lat,
                lon=local.lon,
                date=local.date
            )
            await self.__session.execute(stmt)
            await self.__session.commit()
        else:
            await self.add_aqi(
                request_id=local.request_id,
                aqi=local.aqi,
                pm25=local.pm25,
                pm10=local.pm10,
                o3=local.o3,
                lat=local.lat,
                lon=local.lon,
                date=local.date
            )
