import datetime
from typing import Any

from datetime import datetime, timezone, timedelta

from sqlalchemy import VARCHAR, TIMESTAMP, DECIMAL, INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.api.aqi_converter import AqiConverter
from infrastructure.database.models import Base
from infrastructure.database.models.base import TimestampMixin
from tgbot.services import generate_random_id


class AQILocal(Base, TimestampMixin):
    __tablename__ = "aqi"

    request_id: Mapped[str] = mapped_column(VARCHAR(20), primary_key=True, autoincrement=False)

    aqi: Mapped[int] = mapped_column(INTEGER, default=0, nullable=False, autoincrement=False)

    pm25: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                              autoincrement=False)
    pm10: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                              autoincrement=False)
    o3: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                            autoincrement=False)

    lat: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                        autoincrement=False)

    lon: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                        autoincrement=False)

    date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, autoincrement=False)

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> 'AQILocal':
        pollutants = json["list"][0]["components"]
        aqi_usa: int = AqiConverter.convert_to_usa_aqi(pollutants)[0]  # returns tuple with detailed dict

        timestamp = json["list"][0]["dt"]
        date = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=5)))
        coord = json["coord"]

        return cls(
            request_id=generate_random_id(15),
            aqi=aqi_usa,
            pm25=pollutants.get("pm2_5", 0.0),
            pm10=pollutants.get("pm10", 0.0),
            o3=pollutants.get("o3", 0.0),
            lat=float(coord["lat"]),
            lon=float(coord["lon"]),
            date=date
        )
