
SCHEDULER_AQI_INTERVAL_MINUTES = 5
DEFAULT_THROTTLE_TIME = 1

SUPPORT_USERNAME = "@botik_support"

SET_USER_LANGUAGE_TEXT = "🇷🇺 Выберите язык\n🇺🇿 Tilni tanlang\n🇬🇧 Choose language"

AQI_STATIONS_ID = [
    {
        "name": "Tashkent Chilonzor",
        "with_forecast": True,
        "station_id": "@14722",
        "lat": 41.301911,
        "lng": 69.212345,
    },
    {
        "name": "Tashkent US Embassy",
        "with_forecast": True,
        "station_id": "@11219",
        "lat": 41.376855,
        "lng": 69.239122,
    },
    {
        "name": "Tashkent Yunusabad",
        "with_forecast": True,
        "station_id": "@14723",
        "lat": 41.328069,
        "lng": 69.294476,
    },
    {
        "name": "Tashkent Mirabad",
        "with_forecast": False,
        "station_id": "A361171"
    },
    # {
    #     "name": "Tashkent TV tower",
    #     "with_forecast": False,
    #     "station_id": "A370516"
    # },
]

pollution_levels_emoji = {
        0: "🟢",
        1: "🟡",
        2: "🟠",
        3: "🔴",
        4: "🟤",
        5: "⚫️",
}
