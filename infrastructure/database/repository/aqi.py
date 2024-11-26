from typing import List

from sqlalchemy import select, delete, update, insert
from infrastructure.api.models import AQIModel
from infrastructure.database.models import CurrentAQI, ForecastAQI
from infrastructure.database.repository.base import BaseRepo


class ApiRepo(BaseRepo):
    async def add_current_aqi(
            self,
            aqi_model: AQIModel
    ):
        stmt = insert(CurrentAQI).values(
            request_id=aqi_model.request_id,
            relevance_date=aqi_model.relevance_date,
            pm25_value=aqi_model.iaqi.pm25,
            pm10_value=aqi_model.iaqi.pm10,
            o3_value=aqi_model.iaqi.o3
        ).prefix_with("OR REPLACE")
        await self.session.execute(stmt)
        await self.session.commit()

    async def add_forecast_aqi(
            self,
            aqi_model: AQIModel
    ):
        forecast_dicts = [
            {
                "request_id": forecast.request_id,
                "forecast_date": forecast.day,
                "pm25_forecast_value": forecast.pm25,
                "pm10_forecast_value": forecast.pm10,
                "o3_forecast_value": forecast.o3
            }
            for forecast in aqi_model.forecast.forecast_list
        ]
        stmt = insert(ForecastAQI).values(forecast_dicts).prefix_with("OR IGNORE")
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_current_aqi(self) -> CurrentAQI:
        stmt = select(CurrentAQI).order_by(CurrentAQI.created_at.desc()).limit(1)
        result = await self.session.scalar(stmt)
        return result

    async def get_forecast_aqi(self) -> List[ForecastAQI]:
        stmt = select(ForecastAQI).order_by(ForecastAQI.forecast_date)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def delete_all_forecast_aqi(self):
        stmt = delete(ForecastAQI)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_current_aqi(
            self,
            new_current_aqi: AQIModel
    ):
        stmt = update(CurrentAQI).where(
            CurrentAQI.request_id == new_current_aqi.request_id
        ).values(
            relevance_date=new_current_aqi.relevance_date,
            pm25_value=new_current_aqi.iaqi.pm25,
            pm10_value=new_current_aqi.iaqi.pm10,
            o3_value=new_current_aqi.iaqi.o3
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_forecast_aqi(
            self,
            new_forecast_aqi: AQIModel
    ):
        await self.delete_all_forecast_aqi()
        await self.add_forecast_aqi(aqi_model=new_forecast_aqi)
