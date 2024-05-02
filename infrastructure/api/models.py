from typing import Dict, Any, List
from datetime import datetime, timedelta

import pytz

from infrastructure.api.exceptions import ApiNoDataException, ApiOutdatedDataException, ApiIncorrectKeyException
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

        if o3 is None:
            o3 = 0.1

        if pm10 is None:
            raise ApiNoDataException(data_type="PM 1.0")
        if pm25 is None:
            raise ApiNoDataException(data_type="PM 2.5")

        return cls(pm10, pm25, o3)


class Time:
    def __init__(
            self,
            s: datetime
    ):
        self.s = s

    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        s = json.get("s", None)

        if s is None:
            raise ApiNoDataException(data_type="time -> s")

        s = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
        tz = pytz.timezone('Asia/Tashkent')
        today = datetime.now()

        if today.astimezone(tz=tz) - s.astimezone(tz=tz) > timedelta(hours=4):
            raise ApiOutdatedDataException()

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
        self.relevance_date = time.s
        self.iaqi = iaqi
        self.forecast = forecast

    @classmethod
    def from_values(
        cls,
        pm25: float,
        pm10: float,
        o3: float,
        relevance_date: datetime,
        forecast_list: List[AQIDayForecast]
    ):
        iaqi = IAQI(pm10=pm10, pm25=pm25, o3=o3)
        time = Time(s=relevance_date)
        full_forecast = AQIFullForecast(forecast_list=forecast_list)
        return cls(iaqi, time, full_forecast)

    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        try:
            time = Time.from_json(json["time"])
            iaqi = IAQI.from_json(json["iaqi"])

            try:
                forecast = AQIFullForecast.from_json(json["forecast"]["daily"])
            except KeyError:
                forecast = AQIFullForecast(forecast_list=[])
                pass

            return cls(iaqi, time, forecast)
        except ApiNoDataException:
            raise
        except KeyError as err:
            raise ApiIncorrectKeyException(key=err.args[0])
        except ApiOutdatedDataException:
            raise
