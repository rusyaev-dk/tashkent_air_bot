from abc import ABC, abstractmethod
from typing import Optional


class UsersRepositoryI(ABC):
    """
    Interface for API repositories.
    """

    @abstractmethod
    async def add_user(self, telegram_id: int,
            full_name: str,
            language: str,
            username: Optional[str] = None,):
        pass

    @abstractmethod
    async def get_user(self, telegram_id: int):
        pass

    @abstractmethod
    async def get_user_language_code(self, telegram_id: int):
        pass

    @abstractmethod
    async def get_all_users(self):
        pass

    @abstractmethod
    async def get_users_count_by_language(self, language_code: str):
        pass

    @abstractmethod
    async def get_users_count(self):
        pass

    @abstractmethod
    async def get_active_users_count(self):
        pass

    @abstractmethod
    async def update_user(self, *clauses,
            **values,):
        pass

    @abstractmethod
    async def delete_all_notifications(self,  telegram_id: int):
        pass

    @abstractmethod
    async def update_user_notifications(self, notifications: list[dict], telegram_id: int):
        pass

    @abstractmethod
    async def get_user_notifications(self,telegram_id: int):
        pass

    @abstractmethod
    async def setup_default_user_notifications(self, telegram_id: int):
        pass
