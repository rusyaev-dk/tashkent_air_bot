import asyncio
from datetime import datetime as dt, timedelta

from typing import List, Tuple, Union

import pytz
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.AQI_api.exceptions import ForecastValueApiError, ResponseApiError, IncorrectAqiValueApiError, \
    OutdatedDataApiError
from infrastructure.models import CurrentAQIModel, ForecastAQIModel
from infrastructure.AQI_api.base import BaseClient
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import Config
from tgbot.misc.constants import AQI_STATIONS_ID
from tgbot.services.broadcaster import broadcast


class AQIApi(BaseClient):
    def __init__(self, api_key: str, **kwargs):
        self._api_key = api_key
        self.base_url = "https://api.waqi.info"
        super().__init__(base_url=self.base_url)

    @staticmethod
    def _forecast_response_deserialization(
            response: dict,
    ) -> Tuple[CurrentAQIModel, List[ForecastAQIModel]]:
        tz = pytz.timezone('Asia/Tashkent')
        data = response["data"]
        current_aqi_time = data["time"]
        current_aqi_relevance_date = dt.strptime(current_aqi_time["s"], '%Y-%m-%d %H:%M:%S')
        current_aqi_data = data["iaqi"]

        today = dt.now()
        # if current_aqi_relevance_date.date() < today.date():
        #     raise OutdatedDataApiError

        if today.astimezone(tz=tz) - current_aqi_relevance_date.astimezone(tz=tz) > timedelta(hours=1):
            current_aqi_object = None
        else:
            current_aqi_object = CurrentAQIModel(
                relevance_date=current_aqi_relevance_date,
                pm25_value=float(current_aqi_data.get("pm25", {}).get("v", None)),
                pm10_value=float(current_aqi_data.get("pm10", {}).get("v", None)),
                o3_value=float(current_aqi_data.get("o3", {}).get("v", None)),
            )

        forecast_data = data.get("forecast", {}).get("daily", {})
        forecast_lengths = [len(forecast_data[key]) for key in ["pm25", "pm10", "o3"]]

        forecast_aqi_objects = []
        for counter in range(min(forecast_lengths)):
            pm25_forecast_day = forecast_data.get("pm25", [])[counter]
            pm10_forecast_day = forecast_data.get("pm10", [])[counter]
            o3_forecast_day = forecast_data.get("o3", [])[counter]

            forecast_date_str = pm25_forecast_day.get("day", None)
            forecast_date_obj = dt.strptime(forecast_date_str, '%Y-%m-%d')

            if forecast_date_obj == today or forecast_date_obj < today:
                continue

            forecast_aqi_object = ForecastAQIModel(
                forecast_date=forecast_date_obj,
                pm25_forecast_value=float(pm25_forecast_day.get("avg", None)),
                pm10_forecast_value=float(pm10_forecast_day.get("avg", None)),
                o3_forecast_value=float(o3_forecast_day.get("avg", None)),
            )

            forecast_aqi_objects.append(forecast_aqi_object)

        # if len(forecast_aqi_objects) == 0:
        #     raise ForecastValueApiError

        return current_aqi_object, forecast_aqi_objects

    @staticmethod
    def _response_deserialization(
            response: dict,
            o3_value: float
    ) -> CurrentAQIModel:
        tz = pytz.timezone('Asia/Tashkent')
        data = response["data"]
        current_aqi_time = data["time"]
        current_aqi_relevance_date: dt = dt.strptime(current_aqi_time["s"], '%Y-%m-%d %H:%M:%S')
        current_aqi_data = data["iaqi"]

        today: dt = dt.now()

        # if current_aqi_relevance_date.date() < today.date():
        #     raise OutdatedDataApiError

        if today.astimezone(tz=tz) - current_aqi_relevance_date.astimezone(tz=tz) > timedelta(hours=1):
            current_aqi_object = None
        else:
            current_aqi_object = CurrentAQIModel(
                relevance_date=current_aqi_relevance_date,
                pm25_value=float(current_aqi_data.get("pm25", {}).get("v", None)),
                pm10_value=float(current_aqi_data.get("pm10", {}).get("v", None)),
                o3_value=o3_value,
            )
        return current_aqi_object

    @staticmethod
    def _current_aqi_approximation(
            current_aqi_objects: List[CurrentAQIModel]
    ) -> CurrentAQIModel:

        pm25_approx_current_value = 0
        pm10_approx_current_value = 0
        o3_approx_current_value = 0
        latest_relevance_date = None

        responses_quantity = len(current_aqi_objects)

        for current_aqi in current_aqi_objects:
            pm25_approx_current_value += current_aqi.pm25_value
            pm10_approx_current_value += current_aqi.pm10_value
            o3_approx_current_value += current_aqi.o3_value

            if latest_relevance_date is None or current_aqi.relevance_date > latest_relevance_date:
                latest_relevance_date = current_aqi.relevance_date

        current_aqi_approx_object = CurrentAQIModel(
            relevance_date=latest_relevance_date,
            pm25_value=pm25_approx_current_value / responses_quantity,
            pm10_value=pm10_approx_current_value / responses_quantity,
            o3_value=o3_approx_current_value / responses_quantity,
        )
        return current_aqi_approx_object

    @staticmethod
    def _forecast_aqi_approximation(
            forecast_aqi_lists: List[List[ForecastAQIModel]]
    ) -> List[ForecastAQIModel]:

        approximated_forecast_aqi_objects = []
        min_length = min(len(inner_array) for inner_array in forecast_aqi_lists if inner_array)

        # Перебор по индексам дней в прогнозе
        for day_index in range(min_length):
            total_pm25 = 0
            total_pm10 = 0
            total_o3 = 0

            # Перебор по прогнозам для каждого дня
            for forecast_aqi_list in forecast_aqi_lists:
                # Проверка наличия прогноза для текущего дня
                if day_index < len(forecast_aqi_list):
                    total_pm25 += forecast_aqi_list[day_index].pm25_forecast_value
                    total_pm10 += forecast_aqi_list[day_index].pm10_forecast_value
                    total_o3 += forecast_aqi_list[day_index].o3_forecast_value

            avg_pm25 = total_pm25 / len(forecast_aqi_lists)
            avg_pm10 = total_pm10 / len(forecast_aqi_lists)
            avg_o3 = total_o3 / len(forecast_aqi_lists)

            average_forecast_aqi = ForecastAQIModel(
                request_id=forecast_aqi_lists[0][day_index].request_id,
                forecast_date=forecast_aqi_lists[0][day_index].forecast_date,  # Взяли дату из первого прогноза
                pm25_forecast_value=avg_pm25,
                pm10_forecast_value=avg_pm10,
                o3_forecast_value=avg_o3
            )

            approximated_forecast_aqi_objects.append(average_forecast_aqi)

        return approximated_forecast_aqi_objects

    @staticmethod
    async def _responses_relevance_check(
        responses: List,
        previous_aqi_relevance_date: dt,
        config: Config,
        bot: Bot
    ) -> bool:
        outdated_data_count = 0
        try:
            for response in responses:
                response_date = dt.strptime(response[1]["data"]["time"]["s"], '%Y-%m-%d %H:%M:%S')
                if response_date <= previous_aqi_relevance_date:
                    outdated_data_count += 1
        except KeyError as err:
            await broadcast(bot, users=config.tg_bot.admin_ids,
                            text=f"Ошибка ключа при проверке актуальности: {err}")
            return False

        if outdated_data_count == len(responses):
            return False
        return True

    async def _responses_processing(
            self,
            responses: List,
            responses_with_forecast: List,
            config: Config,
            bot: Bot,
    ) -> Union[Tuple[List, List], None]:
        current_aqi_objects: List[CurrentAQIModel] = []
        forecast_aqi_objects: List[List[ForecastAQIModel]] = []

        try:
            for response in responses_with_forecast:
                try:
                    aqi_objects = self._forecast_response_deserialization(
                        response=response[1],
                    )
                    if aqi_objects[0]:
                        current_aqi_objects.append(aqi_objects[0])
                    forecast_aqi_objects.append(aqi_objects[1])
                except OutdatedDataApiError:
                    continue
                except IncorrectAqiValueApiError:
                    continue

            for response in responses:
                try:
                    current_aqi_obj = self._response_deserialization(
                        response=response[1],
                        o3_value=current_aqi_objects[0].o3_value if len(current_aqi_objects) > 0 else 0.1
                    )
                    if current_aqi_obj:
                        current_aqi_objects.append(current_aqi_obj)
                except OutdatedDataApiError:
                    continue
                except IncorrectAqiValueApiError:
                    continue
        except KeyError as err:
            await broadcast(bot, users=config.tg_bot.admin_ids,
                            text=f"Ошибка ключа при десериализации: {err}")
            return
        except ForecastValueApiError as err:
            await broadcast(bot, users=config.tg_bot.admin_ids, text=err)
            return
        except IncorrectAqiValueApiError as err:
            await broadcast(bot, users=config.tg_bot.admin_ids, text=err)
            return

        return current_aqi_objects, forecast_aqi_objects

    async def _get_responses_with_forecast(self) -> List:
        params = {
            "token": self._api_key
        }

        responses = []
        response_err_counter = 0
        stations_with_forecast = [station for station in AQI_STATIONS_ID if station.get("with_forecast")]
        for station in stations_with_forecast:
            url = f"/feed/{station.get('station_id')}/"
            response = await self._make_request(url=url, method="GET", params=params)
            if response[0] != 200:
                response_err_counter += 1
                if response_err_counter == len(stations_with_forecast):
                    raise ResponseApiError(response_code=response[0])
            await asyncio.sleep(0.05)

            responses.append(response)

        return responses

    async def _get_responses(self) -> List:
        params = {
            "token": self._api_key
        }

        responses = []
        response_err_counter = 0
        stations_without_forecast = [station for station in AQI_STATIONS_ID if not station.get("with_forecast")]
        for station in stations_without_forecast:
            url = f"/feed/{station.get('station_id')}/"
            response = await self._make_request(url=url, method="GET", params=params)
            if response[0] != 200:
                response_err_counter += 1
                if response_err_counter == len(stations_without_forecast):
                    raise ResponseApiError(response_code=response[0])
            await asyncio.sleep(0.05)

            responses.append(response)

        return responses

    async def update_aqi(
            self,
            bot: Bot,
            config: Config,
            session_pool: async_sessionmaker
    ):
        async with session_pool() as session:
            repo = RequestsRepo(session)
            previous_aqi = await repo.aqi.get_current_aqi()
            prev_aqi_exists = True if previous_aqi else False

            try:
                responses_with_forecast = await self._get_responses_with_forecast()
                responses = await self._get_responses()
            except ResponseApiError as err:
                await broadcast(bot, users=config.tg_bot.admin_ids,
                                text=f"🛠 Ошибка запроса: response_code = {err.response_code}")
                return

            if prev_aqi_exists:
                is_relevance = await self._responses_relevance_check(
                    responses=responses_with_forecast+responses,
                    previous_aqi_relevance_date=previous_aqi.relevance_date,
                    config=config, bot=bot
                )
                if not is_relevance:
                    return

            processed = await self._responses_processing(
                responses=responses, responses_with_forecast=responses_with_forecast,
                config=config, bot=bot
            )

            if not processed or (len(processed[0]) == 0 and len(processed[1]) == 0):
                return

            current_aqi_approx_object = self._current_aqi_approximation(current_aqi_objects=processed[0])
            forecast_aqi_approx_objects = self._forecast_aqi_approximation(forecast_aqi_lists=processed[1])

            request_id = previous_aqi.request_id if previous_aqi else None
            current_aqi_approx_object.set_request_id(request_id=request_id)

            if prev_aqi_exists:
                await repo.aqi.update_current_aqi(new_current_aqi=current_aqi_approx_object)
            else:
                await repo.aqi.add_current_aqi(current_aqi=current_aqi_approx_object)

            await repo.aqi.add_forecast_aqi(forecast_objects=forecast_aqi_approx_objects)
            await session.commit()
