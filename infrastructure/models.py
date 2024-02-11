import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass

from infrastructure.AQI_api.exceptions import IncorrectAqiValueApiError
from tgbot.services import generate_random_id


@dataclass
class BaseAQIModel(ABC):
    @abstractmethod
    def __init__(self):
        pass


@dataclass
class CurrentAQIModel(BaseAQIModel):
    request_id: str
    relevance_date: datetime
    pm25_value: float
    pm10_value: float
    o3_value: float

    def __init__(
            self,
            relevance_date: datetime,
            pm25_value: float,
            pm10_value: float,
            o3_value: float,
    ):
        if any(value is None or value <= 0 for value in [pm25_value, pm10_value, o3_value]):
            raise IncorrectAqiValueApiError("Одно из значений current_aqi меньше или равно 0.")

        self.relevance_date = relevance_date
        self.pm25_value = pm25_value
        self.pm10_value = pm10_value
        self.o3_value = o3_value

    def set_request_id(
            self,
            request_id: str = None
    ):
        self.request_id = request_id if request_id else generate_random_id(5)


@dataclass
class ForecastAQIModel(BaseAQIModel):
    request_id: str
    forecast_date: datetime
    pm25_forecast_value: float
    pm10_forecast_value: float
    o3_forecast_value: float

    def __init__(
            self,
            forecast_date: datetime,
            pm25_forecast_value: float,
            pm10_forecast_value: float,
            o3_forecast_value: float,
            request_id: str = None
    ):
        if any(value is None or value <= 0 for value in [pm25_forecast_value, pm10_forecast_value, o3_forecast_value]):
            raise IncorrectAqiValueApiError("Одно из значений forecast_aqi меньше или равно 0.")

        self.request_id = request_id if request_id else generate_random_id(5)
        self.forecast_date = forecast_date
        self.pm25_forecast_value = pm25_forecast_value
        self.pm10_forecast_value = pm10_forecast_value
        self.o3_forecast_value = o3_forecast_value
