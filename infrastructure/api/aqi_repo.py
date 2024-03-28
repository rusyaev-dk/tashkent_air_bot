import asyncio
import logging

from datetime import datetime
from typing import List, Dict, Any

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.api.aqi_client import AQIClient
from infrastructure.api.exceptions import ApiResponseCodeException, ApiNoDataException, \
    ApiOutdatedDataException
from infrastructure.api.models import AQIModel, AQIDayForecast
from infrastructure.database.repository.requests import RequestsRepo
from tgbot.config import Config
from tgbot.services.broadcaster import broadcast


class AQIApiRepo:
    __aqi_stations: List[Dict[str, Any]] = [
        {
            "name": "Tashkent Chilonzor",
            "with_forecast": True,
            "station_id": "@14722",
            "lat": 41.301911,
            "lng": 69.212345,
        },
        {
            "name": "Tashkent US Embassy",
            "with_forecast": True,
            "station_id": "@11219",
            "lat": 41.376855,
            "lng": 69.239122,
        },
        {
            "name": "Tashkent Yunusabad",
            "with_forecast": True,
            "station_id": "@14723",
            "lat": 41.328069,
            "lng": 69.294476,
        },
        {
            "name": "Tashkent Mirabad",
            "with_forecast": False,
            "station_id": "A361171"
        },
        {
            "name": "TIS",
            "with_forecast": False,
            "station_id": "A253081"
        }
        # {
        #     "name": "Osiyo street",
        #     "with_forecast": False,
        #     "station_id": "A370516"
        # },
    ]

    def __init__(self, api_key: str, **kwargs):
        self.__aqi_client = AQIClient(api_key=api_key)

    async def _get_aqi_models(self) -> List[AQIModel]:
        responses: List[Dict[str, Any]] = []
        for aqi_station in self.__aqi_stations:
            try:
                response = await self.__aqi_client.get_aqi_response(station_id=aqi_station.get("station_id"))
                responses.append(response)
                await asyncio.sleep(0.1)
            except ApiResponseCodeException as exception:
                logging.error(msg=exception)
                continue

        if len(responses) == 0:
            return []

        aqi_models: List[AQIModel] = []
        for response in responses:
            try:
                aqi_model = AQIModel.from_json(response["data"])
                aqi_models.append(aqi_model)
            except ApiOutdatedDataException as exception:
                logging.error(msg=exception)
                continue
            except ApiNoDataException as exception:
                logging.error(msg=exception)
                continue

        return aqi_models

    @staticmethod
    def _are_relevance(
            prev_aqi_date: datetime,
            aqi_models: List[AQIModel]
    ) -> bool:
        outdated_count = 0
        for aqi_model in aqi_models:
            if aqi_model.relevance_date < prev_aqi_date:
                outdated_count += 1

        return outdated_count == len(aqi_models)

    @staticmethod
    def _models_data_approximation(
            aqi_models: List[AQIModel]
    ) -> AQIModel:

        models_list_length = len(aqi_models)
        forecast_list_length = len(aqi_models[0].forecast.forecast_list)

        approx_pm25: float = aqi_models[0].iaqi.pm25
        approx_pm10: float = aqi_models[0].iaqi.pm10
        approx_o3: float = aqi_models[0].iaqi.o3
        latest_date: datetime = aqi_models[0].relevance_date

        approx_forecast_pm25: float = 0
        approx_forecast_pm10: float = 0
        approx_forecast_o3: float = 0

        for aqi_model in aqi_models[1:]:  # вычисление среднего значения для текущего индекса
            if latest_date or aqi_model.relevance_date > latest_date:
                latest_date = aqi_model.relevance_date

            approx_pm25 += aqi_model.iaqi.pm25
            approx_pm10 += aqi_model.iaqi.pm10
            approx_o3 += aqi_model.iaqi.o3

        approx_forecast_list: List[AQIDayForecast] = []
        if forecast_list_length != 0:

            day_index = 0
            for i in range(models_list_length):  # вычисление среднего значения для прогноза
                for j in range(models_list_length):
                    approx_forecast_pm25 += aqi_models[j].forecast.forecast_list[day_index].pm25
                    approx_forecast_pm10 += aqi_models[j].forecast.forecast_list[day_index].pm10
                    approx_forecast_o3 += aqi_models[j].forecast.forecast_list[day_index].o3

                approx_forecast_pm25 /= len(aqi_models[i].forecast.forecast_list)
                approx_forecast_pm10 /= len(aqi_models[i].forecast.forecast_list)
                approx_forecast_o3 /= len(aqi_models[i].forecast.forecast_list)

                approx_forecast_day = AQIDayForecast(
                    day=aqi_models[0].forecast.forecast_list[day_index].day,
                    pm25=approx_forecast_pm25,
                    pm10=approx_forecast_pm10,
                    o3=approx_forecast_o3,
                )

                approx_forecast_list.append(approx_forecast_day)
                day_index += 1

        approx_aqi_model = AQIModel.from_values(
            pm25=approx_pm25 / models_list_length,
            pm10=approx_pm10 / models_list_length,
            o3=approx_o3 / models_list_length,
            relevance_date=latest_date,
            forecast_list=approx_forecast_list,
        )

        return approx_aqi_model

    async def update_aqi(
            self,
            bot: Bot,
            config: Config,
            session_pool: async_sessionmaker
    ):
        aqi_models: List[AQIModel] = await self._get_aqi_models()
        if len(aqi_models) == 0:
            logging.error(msg="AQI models list is empty.")
            await broadcast(
                bot=bot,
                users=config.tg_bot.admin_ids,
                text=f"🛠 AQI models list is empty."
            )
            return

        async with session_pool() as session:
            repo = RequestsRepo(session)
            previous_aqi = await repo.aqi.get_current_aqi()
            prev_aqi_exists = True if previous_aqi else False

            if prev_aqi_exists and not self._are_relevance(prev_aqi_date=previous_aqi.relevance_date,
                                                           aqi_models=aqi_models):
                logging.error(msg="AQI models are not relevance")
                await broadcast(
                    bot=bot,
                    users=config.tg_bot.admin_ids,
                    text=f"🛠 AQI models are not relevance."
                )
                return

            approximated_aqi_model = self._models_data_approximation(aqi_models=aqi_models)
            has_forecast: bool = len(approximated_aqi_model.forecast.forecast_list) > 0

            if prev_aqi_exists:
                await repo.aqi.update_current_aqi(new_current_aqi=approximated_aqi_model)
                if has_forecast:
                    await repo.aqi.update_forecast_aqi(new_forecast_aqi=approximated_aqi_model)
                await session.commit()
                return

            await repo.aqi.add_current_aqi(aqi_model=approximated_aqi_model)

            if has_forecast:
                await repo.aqi.add_forecast_aqi(aqi_model=approximated_aqi_model)
            await session.commit()
