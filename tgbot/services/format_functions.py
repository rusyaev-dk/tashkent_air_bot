from infrastructure.database.models import CurrentAQI, ForecastAQI
from infrastructure.database.repo.requests import RequestsRepo
from l10n.translator import LocalizedTranslator
from tgbot.misc.constants import pollution_levels_emoji


def format_current_aqi_info(
        current_aqi: CurrentAQI,
        l10n: LocalizedTranslator
) -> str:
    key = int(current_aqi.pm25_value // 50)
    key = key if key <= 5 else 5

    pollution_level = l10n.get_text(key=f"pollution-level-{key}")
    pollution_level_emoji = pollution_levels_emoji[key]
    health_implications = l10n.get_text(key=f"health-implications-{key}")

    date = current_aqi.relevance_date.strftime('%d').lstrip('0')
    month_number = int(current_aqi.relevance_date.strftime('%m')) - 1
    month = l10n.get_text(key=f"month-full-{month_number}")
    time = current_aqi.relevance_date.strftime('%H:%M')

    args = {
        "pm25_value": int(current_aqi.pm25_value),
        "pm10_value": int(current_aqi.pm10_value),
        "o3_value": str(round(current_aqi.o3_value, 1)),
        "pollution_level_emoji": pollution_level_emoji,
        "pollution_level": pollution_level,
        "health_implications": health_implications,
        "date": date,
        "month": month,
        "time": time
    }
    text = l10n.get_text(key="current-aqi", args=args)

    return text


def format_forecast_aqi_info(
        forecast_list: list[ForecastAQI],
        l10n: LocalizedTranslator
) -> str:
    header_text = l10n.get_text(key="forecast-aqi-header")
    text = f"{header_text}\n"

    for forecast_aqi in forecast_list:
        key = int(forecast_aqi.pm25_forecast_value // 50)
        key = key if key <= 5 else 5

        date = forecast_aqi.forecast_date.strftime('%d').lstrip('0')
        month_number = int(forecast_aqi.forecast_date.strftime('%m')) - 1
        month = l10n.get_text(key=f"month-full-{month_number}")

        pollution_level = l10n.get_text(key=f"pollution-level-{key}")
        pollution_level_emoji = pollution_levels_emoji[key]

        args = {
            "date": date,
            "month": month,
            "pm25_forecast_value": int(forecast_aqi.pm25_forecast_value),
            "pm10_forecast_value": int(forecast_aqi.pm10_forecast_value),
            "o3_forecast_value": str(round(forecast_aqi.o3_forecast_value, 1)),
            "pollution_level_emoji": pollution_level_emoji,
            "pollution_level": pollution_level
        }

        forecast_text = l10n.get_text(key="forecast-aqi", args=args)
        text += f"\n{forecast_text}\n"

    return text


def format_reference_text(
        l10n: LocalizedTranslator
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
        repo: RequestsRepo
) -> str:
    total_users_count = await repo.users.get_users_count()
    active_users_count = await repo.users.get_active_users_count()
    ru_users_count = await repo.users.get_users_count_by_language(language_code="ru")
    uz_users_count = await repo.users.get_users_count_by_language(language_code="uz")
    en_users_count = await repo.users.get_users_count_by_language(language_code="en")

    text = (
        f"Всего пользователей: <b>{total_users_count}</b> чел.\n"
        f"Активных пользователей: <b>{active_users_count}</b> чел.\n\n"
        f"Распределение по языкам:\n"
        f"🇷🇺: <b>{ru_users_count}</b> чел. <b>~{int(ru_users_count / total_users_count * 100)}%</b>\n"
        f"🇺🇿: <b>{uz_users_count}</b> чел. <b>~{int(uz_users_count / total_users_count * 100)}%</b>\n"
        f"🇬🇧: <b>{en_users_count}</b> чел. <b>~{int(en_users_count / total_users_count * 100)}%</b>\n"
    )

    return text
