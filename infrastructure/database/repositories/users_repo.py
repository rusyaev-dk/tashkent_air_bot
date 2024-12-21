from typing import Optional

from sqlalchemy import select, func, update, delete, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models import UserLocal, UserNotification
from tgbot.services import generate_random_id


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def add_user(
            self,
            telegram_id: int,
            full_name: str,
            language_code: str,
            username: Optional[str] = None,
    ) -> UserLocal:
        stmt = (
            insert(UserLocal)
            .values(
                telegram_id=telegram_id,
                full_name=full_name,
                language_code=language_code,
                username=username,
            )
            .on_conflict_do_update(
                index_elements=[UserLocal.telegram_id],
                set_={
                    "full_name": full_name,
                    "language_code": language_code,
                    "username": username
                }
            )
            .returning(UserLocal)
        )
        result = await self.__session.execute(stmt)
        await self.__session.commit()

        return result.scalar_one()

    async def get_user(self, telegram_id: int) -> Optional[UserLocal]:
        stmt = select(UserLocal).where(UserLocal.telegram_id == telegram_id)
        result = await self.__session.scalar(stmt)
        return result

    async def get_user_language_code(self, telegram_id: int) -> str:
        stmt = select(UserLocal.language_code).where(UserLocal.telegram_id == telegram_id)
        result = await self.__session.scalar(stmt)
        return result

    async def get_users(self, *clauses) -> list[UserLocal]:
        stmt = select(UserLocal).where(*clauses)
        result = await self.__session.execute(stmt)
        return result.scalars().all()

    async def get_users_count(self, *clauses) -> int:
        stmt = select(func.count(UserLocal.telegram_id)).where(*clauses)
        result = await self.__session.scalar(stmt)
        return result or 0

    async def get_users_count_by_language(self, language_code: str) -> int:
        stmt = select(func.count(
            and_(UserLocal.language_code == language_code,
                 UserLocal.is_active == True)
        ))
        result = await self.__session.scalar(stmt)
        return result or 0

    async def update_user(
            self,
            *clauses,
            **values,
    ) -> None:
        stmt = update(UserLocal).where(*clauses).values(**values)
        await self.__session.execute(stmt)
        await self.__session.commit()

    async def delete_all_notifications(self, telegram_id: int) -> None:
        stmt = delete(UserNotification).where(UserNotification.telegram_id == telegram_id)
        await self.__session.execute(stmt)
        await self.__session.commit()

    async def update_user_notifications(
        self,
        hours: list[str],
        telegram_id: int,
    ) -> None:
        await self.delete_all_notifications(telegram_id=telegram_id)

        if len(hours) > 0:
            notification_time_dicts = [
                {
                    "notification_id": generate_random_id(length=5, prefix=str(telegram_id)),
                    "telegram_id": telegram_id,
                    "hours": hour,
                    "minutes": "00",
                }
                for hour in hours
            ]

            stmt = insert(UserNotification).values(notification_time_dicts)
            await self.__session.execute(stmt)

        await self.update_user(
            UserLocal.telegram_id == telegram_id,
            notifications=bool(len(hours)),
        )
        await self.__session.commit()

    async def get_user_notification_hours(self, telegram_id: int) -> set:
        stmt = select(UserNotification).where(UserNotification.telegram_id == telegram_id)
        result = await self.__session.execute(stmt)

        hours_set = set()
        for notification in result.scalars().all():
            hours_set.add(notification.hours)

        return hours_set

    async def setup_default_user_notifications(self, telegram_id: int) -> None:
        await self.update_user_notifications(
            telegram_id=telegram_id,
            hours=["08", "13", "18"],
        )

    async def get_notifiable_users_ids(
            self,
            hours: str,
            language_code: str = None
    ) -> list[int]:
        conditions = [
            UserLocal.is_active == True,
            UserLocal.notifications == True,
            UserNotification.hours == hours,
        ]
        if language_code:
            conditions.append(UserLocal.language_code == language_code)

        stmt = select(UserLocal.telegram_id).join(
            UserNotification, UserNotification.telegram_id == UserLocal.telegram_id
        ).where(and_(*conditions))

        result = await self.__session.scalars(stmt)
        return list(result.all())
