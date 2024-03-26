from typing import Optional, List, Dict

from sqlalchemy import select, func, update, delete, and_
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import User, UserNotification
from infrastructure.database.repository.base import BaseRepository
from tgbot.services import generate_random_id


class UserRepository(BaseRepository):
    async def add_user(
        self,
        telegram_id: int,
        full_name: str,
        language: str,
        username: Optional[str] = None,
    ) -> User:
        stmt = (
            insert(User)
            .values(
                telegram_id=telegram_id,
                full_name=full_name,
                language=language,
                username=username,
            )
            .on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_={
                    "full_name": full_name,
                    "language": language,
                    "username": username
                }
            )
            .returning(User)
        )
        result = await self.session.execute(stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_user(
            self,
            telegram_id: int
    ) -> User:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.scalar(stmt)
        return result

    async def get_user_language_code(
            self,
            telegram_id: int
    ) -> str:
        stmt = select(User.language).where(User.telegram_id == telegram_id)
        result = await self.session.scalar(stmt)
        return result

    async def get_all_users(
            self,
            language_code: str = None
    ):
        if language_code:
            stmt = select(User).where(User.language == language_code)
        else:
            stmt = select(User)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_notifiable_user_ids(
            self,
            hours: str,
            language_code: str = None,
    ) -> List[int]:

        stmt = select(User.telegram_id).join(
            UserNotification, UserNotification.telegram_id == User.telegram_id
        ).where(
            and_(
                User.is_active == True,
                User.notifications == True,
                UserNotification.hours == hours,
                (User.language == language_code) if language_code else (User.language != None)
            )
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def get_users_count(self) -> int:
        stmt = select(func.count(User.telegram_id))
        result = await self.session.scalar(stmt)
        return result

    async def get_active_users_count(self) -> int:
        stmt = select(func.count(User.telegram_id)).where(User.is_active == True)
        result = await self.session.scalar(stmt)
        return result

    async def get_users_count_by_language(self, language_code: str) -> int:
        stmt = select(func.count(User.telegram_id)).where(User.language == language_code)
        result = await self.session.scalar(stmt)
        return result

    async def update_user(
            self,
            *clauses,
            **values,
    ):
        stmt = update(User).where(*clauses).values(**values)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_all_notifications(
            self,
            telegram_id: int
    ):
        stmt = delete(UserNotification).where(UserNotification.telegram_id == telegram_id)
        await self.session.execute(stmt)

    async def update_user_notifications(
            self,
            notifications: List[Dict],
            telegram_id: int,
    ):
        await self.delete_all_notifications(telegram_id=telegram_id)
        if len(notifications) > 0:
            notification_time_dicts = [
                {
                    "notification_id": str(telegram_id) + "_" + notification.get("notification_id"),
                    "telegram_id": telegram_id,
                    "hours": notification.get("hours"),
                    "minutes": notification.get("minutes"),
                }
                for notification in notifications
            ]
            stmt = insert(UserNotification).values(notification_time_dicts)
            await self.session.execute(stmt)

        await self.update_user(
            User.telegram_id == telegram_id,
            notifications=True if len(notifications) > 0 else False
        )

        await self.session.commit()

    async def get_user_notifications(
            self,
            telegram_id: int
    ) -> List[Dict]:
        stmt = select(UserNotification).where(UserNotification.telegram_id == telegram_id)
        result = await self.session.execute(stmt)

        user_notifications = []
        for notification in result.scalars().all():
            user_notifications.append(
                {
                    "notification_id": notification.hours + generate_random_id(5),
                    "hours": notification.hours,
                    "minutes": notification.minutes,
                    "chosen_by_user": True
                }
            )

        return user_notifications

    async def setup_default_user_notifications(
            self,
            telegram_id: int
    ):
        default_hours = ["08", "13", "18"]
        default_notifications = [
            {
                "notification_id": default_hours[i] + generate_random_id(5),
                "hours": default_hours[i],
                "minutes": "00",
                "chosen_by_user": True
            }
            for i in range(3)
        ]
        await self.update_user_notifications(
            telegram_id=telegram_id,
            notifications=default_notifications
        )
