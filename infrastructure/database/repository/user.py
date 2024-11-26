from typing import Optional, List, Dict

from sqlalchemy import select, func, update, delete
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import User, UserNotification
from infrastructure.database.repository.base import BaseRepo


class UserRepo(BaseRepo):
    async def add_user(
            self,
            telegram_id: int,
            full_name: str,
            language: str,
            username: Optional[str] = None,
    ) -> User:
        stmt = insert(User).values(
            telegram_id=telegram_id,
            full_name=full_name,
            language=language,
            username=username
        ).returning(User)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_user(self, telegram_id: int) -> Optional[User]:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.scalar(stmt)
        return result

    async def get_user_language_code(self, telegram_id: int) -> str:
        stmt = select(User.language).where(User.telegram_id == telegram_id)
        result = await self.session.scalar(stmt)
        return result

    async def get_all_users(self) -> List[User]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_users_count_by_language(self, language_code: str) -> int:
        stmt = select(User).where(User.language == language_code)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def get_users_count(self) -> int:
        stmt = select(func.count(User.telegram_id))
        result = await self.session.scalar(stmt)
        return result

    async def get_active_users_count(self) -> int:
        stmt = select(func.count(User.telegram_id)).where(User.is_active == 1)
        result = await self.session.scalar(stmt)
        return result

    async def update_user(
            self,
            *clauses,
            **values,
    ) -> None:
        stmt = update(User).where(*clauses).values(**values)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_all_notifications(self, telegram_id: int) -> None:
        stmt = delete(UserNotification).where(UserNotification.telegram_id == telegram_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_user_notifications(
        self,
        notifications: List[Dict],
        telegram_id: int,
    ) -> None:
        await self.delete_all_notifications(telegram_id=telegram_id)

        if notifications:
            notification_time_dicts = [
                {
                    "notification_id": f"{telegram_id}_{notification['notification_id']}",
                    "telegram_id": telegram_id,
                    "hours": notification["hours"],
                    "minutes": notification["minutes"],
                }
                for notification in notifications
            ]

            stmt = insert(UserNotification).values(notification_time_dicts)
            await self.session.execute(stmt)

        await self.update_user(
            User.telegram_id == telegram_id,
            notifications=int(bool(notifications)),
        )
        await self.session.commit()

    async def get_user_notifications(self, telegram_id: int) -> List[Dict]:
        stmt = select(UserNotification).where(UserNotification.telegram_id == telegram_id)
        result = await self.session.execute(stmt)

        user_notifications = []
        for notification in result.scalars().all():
            user_notifications.append(
                {
                    "notification_id": notification.notification_id,
                    "hours": notification.hours,
                    "minutes": notification.minutes,
                    "chosen_by_user": True,
                }
            )

        return user_notifications

    async def setup_default_user_notifications(self, telegram_id: int) -> None:
        default_hours = ["08", "13", "18"]
        default_notifications = [
            {
                "notification_id": f"{hour}_{telegram_id}",
                "hours": hour,
                "minutes": "00",
                "chosen_by_user": True,
            }
            for hour in default_hours
        ]

        await self.update_user_notifications(
            telegram_id=telegram_id,
            notifications=default_notifications,
        )
