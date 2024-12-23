import asyncio
import logging
from datetime import datetime, timedelta

from typing import Optional

import pytz
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from infrastructure.api.aqi_converter import AqiConverter
from infrastructure.api.models.aqi import AQI
from infrastructure.api.clients.aqi_client import AQIClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.aqi import AQILocal
from tgbot.services import generate_random_id


class AQIRepository:
    def __init__(self, aqi_client: AQIClient, session: AsyncSession):
        self.__client = aqi_client
        self.__session = session

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

        tz = pytz.timezone("Asia/Tashkent")
        local.date = local.date.astimezone(tz)

        return AQI.from_local(local)

    async def update_aqi(self) -> None:
        aqicn_data = await self.__fetch_aqicn_data()
        owm_data = await self.__fetch_owm_data()

        if not aqicn_data and not owm_data:
            return

        if aqicn_data and owm_data:
            aqi = (aqicn_data.aqi + owm_data.aqi) // 2
            pm25 = (aqicn_data.pm25 + owm_data.pm25) / 2
            pm10 = (aqicn_data.pm10 + owm_data.pm10) / 2
            o3 = (aqicn_data.o3 + owm_data.o3) / 2
            date = aqicn_data.date if aqicn_data.date > owm_data.date else owm_data.date
        elif aqicn_data:
            aqi = aqicn_data.aqi
            pm25 = aqicn_data.pm25
            pm10 = aqicn_data.pm10
            o3 = aqicn_data.o3
            date = aqicn_data.date
        else:
            aqi = owm_data.aqi
            pm25 = owm_data.pm25
            pm10 = owm_data.pm10
            o3 = owm_data.o3
            date = owm_data.date
       
        if await self.get_aqi():
            stmt = update(AQILocal).values(
                aqi=aqi,
                pm25=pm25,
                pm10=pm10,
                o3=o3,
                lat=self.__default_lat,
                lon=self.__default_lon,
                date=date
            )
            await self.__session.execute(stmt)
            await self.__session.commit()
        else:
            await self.add_aqi(
                request_id=generate_random_id(15),
                aqi=aqi,
                pm25=pm25,
                pm10=pm10,
                o3=o3,
                lat=self.__default_lat,
                lon=self.__default_lon,
                date=date
            )

    async def __fetch_aqicn_data(self) -> Optional[AQI]:
        total_aqi, total_pm25, total_pm10, total_o3 = 0, 0, 0, 0
        count = 0
        latest_date = None

        fixed_offset = pytz.FixedOffset(300)
        now = datetime.now(tz=fixed_offset)

        for station_id in self.__aqicn_stations:
            await asyncio.sleep(0.05)
            data = await self.__client.request_aqicn_data(station_id=station_id)
            if not data:
                continue

            try:
                aqi = data.get("aqi")
                time_str = data.get("time", {}).get("s")
                iaqi = data.get("iaqi", {})

                pm25 = float(iaqi.get("pm25", {}).get("v", 0)) if "pm25" in iaqi else None
                pm10 = float(iaqi.get("pm10", {}).get("v", 0)) if "pm10" in iaqi else None
                o3 = float(iaqi.get("o3", {}).get("v", 0)) if "o3" in iaqi else None

            except KeyError as e:
                logging.error(f"KeyError for AQICN data: {e}")
                return None
            except Exception as e:
                logging.error(f"Error for AQICN data: {e}")
                return None

            date = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=fixed_offset)

            # Skipping station if data is older than time threshold
            if not date or (now - date > self.__time_threshold) or now < date:
                continue

            if aqi is not None:
                total_aqi += aqi
            if pm25 is not None:
                pm25 = AqiConverter.get_pm25_concentration(aqi=int(pm25))
                total_pm25 += pm25
            if pm10 is not None:
                pm10 = AqiConverter.get_pm10_concentration(aqi=int(pm10))
                total_pm10 += pm10
            if o3 is not None:
                o3 = AqiConverter.get_o3_concentration(aqi=int(o3))
                total_o3 += o3
            count += 1

            if date and (latest_date is None or date > latest_date):
                latest_date = date

        if count == 0 or latest_date is None:
            return None

        return AQI(
            aqi=int(total_aqi / count),
            pm25=total_pm25 / count,
            pm10=total_pm10 / count,
            o3=total_o3 / count,
            date=latest_date,
            lat=self.__default_lat,
            lon=self.__default_lon
        )

    async def __fetch_owm_data(self) -> Optional[AQI]:
        json = await self.__client.request_owm_data(self.__default_lat, self.__default_lon)
        if not json:
            return None

        try:
            pollutants = json["list"][0]["components"]
            aqi_usa: int = AqiConverter.convert_to_usa_aqi(pollutants)[0]  # returns tuple with detailed dict

            timestamp = json["list"][0]["dt"]
            tz = pytz.timezone("Asia/Tashkent")
            date = datetime.fromtimestamp(timestamp, tz)
            coord = json["coord"]
        except KeyError as e:
            logging.error(f"KeyError for OWM data: {e}")
            return None
        except Exception as e:
            logging.error(f"Error for OWM data: {e}")
            return None

        return AQI(
            aqi=aqi_usa,
            pm25=pollutants.get("pm2_5", 0.0),
            pm10=pollutants.get("pm10", 0.0),
            o3=pollutants.get("o3", 0.0),
            lat=float(coord["lat"]),
            lon=float(coord["lon"]),
            date=date
        )

    __aqicn_stations = [
        "@11219",
        "A477607",
        "@14723",
        "A370516",
        "A486382",
        "@14722",
        "A479296"
    ]

    __default_lat = 41.2646
    __default_lon = 69.2163
    __time_threshold = timedelta(hours=1)
