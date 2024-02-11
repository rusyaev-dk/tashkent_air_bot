from typing import List

from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert

from infrastructure.models import CurrentAQIModel, ForecastAQIModel
from infrastructure.database.models import CurrentAQI, ForecastAQI
from infrastructure.database.repo.base import BaseRepo


class AQIRepo(BaseRepo):
    async def add_current_aqi(
            self,
            current_aqi: CurrentAQIModel
    ):
        stmt = insert(CurrentAQI).values(
            request_id=current_aqi.request_id,
            relevance_date=current_aqi.relevance_date,
            pm25_value=current_aqi.pm25_value,
            pm10_value=current_aqi.pm10_value,
            o3_value=current_aqi.o3_value
        ).on_conflict_do_update(
            index_elements=[CurrentAQI.request_id],
            set_={
                "relevance_date": current_aqi.relevance_date,
                "pm25_value": current_aqi.pm25_value,
                "pm10_value": current_aqi.pm10_value,
                "o3_value": current_aqi.o3_value
            }
        ).returning(CurrentAQI)
        await self.session.execute(stmt)

    async def add_forecast_aqi(
            self,
            forecast_objects: List[ForecastAQIModel]
    ):
        await self.delete_old_forecast()
        forecast_dicts = [
            {
                "request_id": forecast.request_id,
                "forecast_date": forecast.forecast_date,
                "pm25_forecast_value": forecast.pm25_forecast_value,
                "pm10_forecast_value": forecast.pm10_forecast_value,
                "o3_forecast_value": forecast.o3_forecast_value
            }
            for forecast in forecast_objects
        ]
        stmt = insert(ForecastAQI).values(forecast_dicts).on_conflict_do_nothing()
        await self.session.execute(stmt)

    async def get_current_aqi(self) -> CurrentAQI:
        stmt = select(CurrentAQI).order_by(CurrentAQI.created_at.desc()).limit(1)
        result = await self.session.scalar(stmt)
        return result

    async def get_forecast_aqi(self) -> List[ForecastAQI]:
        stmt = select(ForecastAQI).order_by(ForecastAQI.forecast_date)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def update_current_aqi(
            self,
            new_current_aqi: CurrentAQIModel
    ):
        stmt = update(CurrentAQI).where(
            CurrentAQI.request_id == new_current_aqi.request_id
        ).values(
            relevance_date=new_current_aqi.relevance_date,
            pm25_value=new_current_aqi.pm25_value,
            pm10_value=new_current_aqi.pm10_value,
            o3_value=new_current_aqi.o3_value
        )
        await self.session.execute(stmt)

    async def delete_old_forecast(self):
        stmt = delete(ForecastAQI)
        await self.session.execute(stmt)
