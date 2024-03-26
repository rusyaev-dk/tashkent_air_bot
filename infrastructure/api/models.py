from typing import Dict, Any, List
from datetime import datetime

from infrastructure.api.exceptions import ApiIncorrectValueException
from tgbot.services import generate_random_id


class IAQI:
    def __init__(
        self,
        pm10: float,
        pm25: float,
        o3: float,
    ):
        self.pm10 = pm10
        self.pm25 = pm25
        self.o3 = o3

    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        pm10 = json.get("pm10", {}).get("v", None)
        pm25 = json.get("pm25", {}).get("v", None)
        o3 = json.get("o3", {}).get("v", None)

        if pm10 is None or pm25 is None or o3 is None:
            raise ApiIncorrectValueException(incorrect_value=0)

        return cls(pm10, pm25, o3)


class Time:
    def __init__(
            self,
            s: str
    ):
        self.s = s

    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        s = json.get("s", None)

        if s is None:
            raise ApiIncorrectValueException(incorrect_value="_")

        return cls(s)


class AQIDayForecast:
    def __init__(
        self,
        day: str,
        pm25: float,
        pm10: float,
        o3: float
    ):
        self.request_id = generate_random_id(10)
        self.day = day
        self.pm25 = pm25
        self.pm10 = pm10
        self.o3 = o3


class AQIFullForecast:
    def __init__(self, forecast_list: List[AQIDayForecast]):
        self.forecast_list = forecast_list

    @classmethod
    def from_json(cls, json: Dict[str, Any]):

        o3_daily_forecast: List[Dict[str, Any]] = json.get("o3", [])
        pm10_daily_forecast: List[Dict[str, Any]] = json.get("pm10", [])
        pm25_daily_forecast: List[Dict[str, Any]] = json.get("pm25", [])

        min_length = min(len(o3_daily_forecast), len(pm10_daily_forecast), len(pm25_daily_forecast))

        o3_daily_forecast = o3_daily_forecast[:min_length]
        pm10_daily_forecast = pm10_daily_forecast[:min_length]
        pm25_daily_forecast = pm25_daily_forecast[:min_length]

        forecast_list: List[AQIDayForecast] = []
        for i in range(min_length):
            o3_avg = o3_daily_forecast[i].get("avg", None)
            pm10_avg = pm10_daily_forecast[i].get("avg", None)
            pm25_avg = pm25_daily_forecast[i].get("avg", None)
            day = o3_daily_forecast[i].get("day", None)

            if o3_avg is None or pm10_avg is None or pm25_avg is None or day is None:
                continue

            forecast_day = AQIDayForecast(day=day, o3=o3_avg, pm10=pm10_avg, pm25=pm25_avg)
            forecast_list.append(forecast_day)

        return cls(forecast_list)


class AQIModel:
    def __init__(
        self,
        iaqi: IAQI,
        time: Time,
        forecast: AQIFullForecast
    ):
        self.request_id = generate_random_id(length=15)
        self.relevance_date = datetime.strptime(time.s, '%Y-%m-%d %H:%M:%S')
        self.iaqi = iaqi
        self.forecast = forecast

    @classmethod
    def from_values(
        cls,
        pm25: float,
        pm10: float,
        o3: float,
        relevance_date: datetime,
        forecast: AQIFullForecast
    ):
        iaqi = IAQI(pm10=pm10, pm25=pm25, o3=o3)
        time = Time(s=relevance_date.strftime("%Y-%m-%d %H:%M:%S"))
        return cls(iaqi, time, forecast)

    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        try:
            iaqi = IAQI.from_json(json["iaqi"])
            time = Time.from_json(json["time"])
            forecast = AQIFullForecast.from_json(json["forecast"]["daily"])

            return cls(iaqi, time, forecast)
        except ApiIncorrectValueException:
            raise
