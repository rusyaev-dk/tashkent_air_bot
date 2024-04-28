from typing import Dict, List, Any

SCHEDULER_AQI_INTERVAL_MINUTES = 3
DEFAULT_THROTTLE_TIME = 1

SUPPORT_USERNAME = "@botik_support"

SET_USER_LANGUAGE_TEXT = "🇷🇺 Выберите язык\n🇺🇿 Tilni tanlang\n🇬🇧 Choose language"

# AQI_STATIONS_ID: List[Dict[str, Any]] = [
#     {
#         "name": "Tashkent Chilonzor",
#         "with_forecast": True,
#         "station_id": "@14722",
#         "lat": 41.301911,
#         "lng": 69.212345,
#     },
#     {
#         "name": "Tashkent US Embassy",
#         "with_forecast": True,
#         "station_id": "@11219",
#         "lat": 41.376855,
#         "lng": 69.239122,
#     },
#     {
#         "name": "Tashkent Yunusabad",
#         "with_forecast": True,
#         "station_id": "@14723",
#         "lat": 41.328069,
#         "lng": 69.294476,
#     },
#     {
#         "name": "Tashkent Mirabad",
#         "with_forecast": False,
#         "station_id": "A361171"
#     },
#     {
#         "name": "TIS",
#         "with_forecast": False,
#         "station_id": "A253081"
#     }
#     # {
#     #     "name": "Osiyo street",
#     #     "with_forecast": False,
#     #     "station_id": "A370516"
#     # },
# ]

# AQI_STATIONS_BY_DISTRICTS: Dict[str, List[str]] = {
#     "14722": ["shaykhantakhur_district", "uchtepa_district", "chilanzar_district", "yakkasaray_district"],
#     "14723": ["mirzo-ulugbek-district"],
#     "11219": ["yunusabad-district", "almazar-district"],
#     "A361171": ["mirabad-district", "sergeli-district", "", ""]
# }

pollution_levels_emoji = {
        0: "🟢",
        1: "🟡",
        2: "🟠",
        3: "🔴",
        4: "🟤",
        5: "⚫️",
}
