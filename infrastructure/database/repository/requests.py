from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repository.aqi import AQIDBRepo
from infrastructure.database.repository.user import UserDBRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserDBRepo:
        return UserDBRepo(self.session)

    @property
    def aqi(self) -> AQIDBRepo:
        return AQIDBRepo(self.session)
