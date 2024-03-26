from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repository.aqi import AQIDBRepository
from infrastructure.database.repository.user import UserRepository


@dataclass
class DBRequestsRepository:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepository:
        return UserRepository(self.session)

    @property
    def aqi(self) -> AQIDBRepository:
        return AQIDBRepository(self.session)
