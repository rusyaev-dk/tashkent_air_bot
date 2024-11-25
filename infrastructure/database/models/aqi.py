import datetime

from sqlalchemy import VARCHAR, TIMESTAMP, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models import Base
from infrastructure.database.models.base import TimestampMixin


class CurrentAQI(Base, TimestampMixin):
    __tablename__ = "current_aqi"

    request_id: Mapped[str] = mapped_column(VARCHAR(20), primary_key=True, autoincrement=False)

    relevance_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, autoincrement=False)
    pm25_value: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                              autoincrement=False)
    pm10_value: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                              autoincrement=False)
    o3_value: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                            autoincrement=False)


class ForecastAQI(Base, TimestampMixin):
    __tablename__ = "forecast_aqi"

    request_id: Mapped[str] = mapped_column(VARCHAR(5), primary_key=True, autoincrement=False)

    forecast_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, autoincrement=False)
    pm25_forecast_value: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                                       autoincrement=False)
    pm10_forecast_value: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                                       autoincrement=False)
    o3_forecast_value: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4), default=0, nullable=False,
                                                     autoincrement=False)
