from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repository.user import UserRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)
