from datetime import datetime

from sqlalchemy import VARCHAR, TIMESTAMP, DECIMAL, INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models import Base
from infrastructure.database.models.base import TimestampMixin


class AQILocal(Base, TimestampMixin):
    __tablename__ = "aqi"

    request_id: Mapped[str] = mapped_column(VARCHAR(20), primary_key=True, autoincrement=False)

    aqi: Mapped[int] = mapped_column(INTEGER, default=0, nullable=False,
                                     autoincrement=False)

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

    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                           autoincrement=False)
