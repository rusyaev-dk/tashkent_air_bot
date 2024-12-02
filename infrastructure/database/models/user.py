from typing import Optional

from sqlalchemy import String, BOOLEAN
from sqlalchemy import text, BIGINT
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base, TimestampMixin


class UserLocal(Base, TimestampMixin):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    notifications: Mapped[bool] = mapped_column(BOOLEAN, default=True, autoincrement=False)
    language_code: Mapped[str] = mapped_column(String(10), server_default=text("'ru'"))
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True, autoincrement=False)

    def __repr__(self):
        return f"<User {self.telegram_id} {self.username} {self.full_name}>"


class UserNotification(Base):
    __tablename__ = "user_notifications"

    notification_id: Mapped[str] = mapped_column(String(32), primary_key=True, autoincrement=False)
    telegram_id: Mapped[int] = mapped_column(BIGINT, primary_key=False, autoincrement=False)
    hours: Mapped[str] = mapped_column(String(16), autoincrement=False)
    minutes: Mapped[str] = mapped_column(String(16), autoincrement=False)
