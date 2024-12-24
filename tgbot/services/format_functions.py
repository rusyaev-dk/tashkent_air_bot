from infrastructure.api.models.aqi import AQI
from infrastructure.database.models import UserLocal

from infrastructure.database.repositories.users_repo import UsersRepository
from l10n.translator import Translator
from tgbot.misc.constants import pollution_levels_emoji


def format_aqi_info(
        aqi: AQI,
        l10n: Translator,
        locale: str = None
) -> str:
    key = get_key(aqi.aqi)

    pollution_level = l10n.get_text(key=f"pollution-level-{key}", locale=locale)
    pollution_level_emoji = pollution_levels_emoji[key]
    health_implications = l10n.get_text(key=f"health-implications-{key}", locale=locale)

    date = aqi.date.strftime('%d').lstrip('0')
    month_number = int(aqi.date.strftime('%m')) - 1
    month = l10n.get_text(key=f"month-full-{month_number}", locale=locale)
    time = aqi.date.strftime('%H:%M')

    args = {
        "aqi": int(aqi.aqi),
        "pm25": int(aqi.pm25),
        "pollution_level_emoji": pollution_level_emoji,
        "pollution_level": pollution_level,
        "health_implications": health_implications,
        "date": date,
        "month": month,
        "time": time
    }
    text = l10n.get_text(key="current-aqi", args=args, locale=locale)

    return text


def get_key(aqi_value: int) -> int:
    if 0 <= aqi_value <= 50:
        return 0  # Загрязнение минимально
    elif 51 <= aqi_value <= 100:
        return 1  # Удовлетворительно
    elif 101 <= aqi_value <= 150:
        return 2  # Вредно для уязвимых групп
    elif 151 <= aqi_value <= 200:
        return 3  # Вредно
    elif 201 <= aqi_value <= 300:
        return 4  # Очень вредно
    else:
        return 5


def format_reference_text(
        l10n: Translator
):
    args = {}

    for i in range(1, 5):
        key_prefix = f"article_{i}"
        link_key = f"article-{i}-link"
        name_key = f"article-{i}-name"

        args[key_prefix] = f"<a href='{l10n.get_text(key=link_key)}'><b>{l10n.get_text(key=name_key)}</b></a>"

    text = l10n.get_text(key="reference", args=args)

    return text


async def format_statistics_info(
        users_repo: UsersRepository
) -> str:

    total_users_count = await users_repo.get_users_count()
    active_users_count = await users_repo.get_users_count(UserLocal.is_active == True)

    ru_users_count = await users_repo.get_users_count_by_language(language_code="ru")
    uz_users_count = await users_repo.get_users_count_by_language(language_code="uz")
    en_users_count = await users_repo.get_users_count_by_language(language_code="en")

    text = (
        f"Всего пользователей: <b>{total_users_count}</b> чел.\n"
        f"Активных пользователей: <b>{active_users_count}</b> чел.\n\n"
        f"Распределение по языкам:\n"
        f"🇷🇺: <b>{ru_users_count}</b> чел. <b>~{int(ru_users_count / active_users_count * 100)}%</b>\n"
        f"🇺🇿: <b>{uz_users_count}</b> чел. <b>~{int(uz_users_count / active_users_count * 100)}%</b>\n"
        f"🇬🇧: <b>{en_users_count}</b> чел. <b>~{int(en_users_count / active_users_count * 100)}%</b>\n"
    )

    return text
