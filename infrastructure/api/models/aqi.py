from datetime import datetime, timezone, timedelta

from infrastructure.database.models.aqi import AQILocal


class AQI:
    def __init__(
        self,
        aqi: int,
        pm10: float,
        pm25: float,
        o3: float,
        lat: float,
        lon: float,
        date: datetime,
    ):
        self.pm10 = pm10
        self.pm25 = pm25
        self.o3 = o3
        self.aqi = aqi
        self.lat = lat
        self.lon = lon
        self.date = date

    @classmethod
    def from_local(cls, local: AQILocal) -> 'AQI':
        date = local.date.replace(tzinfo=timezone(timedelta(hours=5)))

        return cls(
            aqi=local.aqi,
            pm10=local.pm10,
            pm25=local.pm25,
            o3=local.o3,
            lat=local.lat,
            lon=local.lon,
            date=date,
        )
