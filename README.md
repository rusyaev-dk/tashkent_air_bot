# :cityscape: Tashkent air Bot
Tashkent air Bot is a Telegram bot designed to provide real-time information about air quality index (AQI) in Tashkent city.

## Screenshots

![Main menu](/screenshots/tashkent_air_bot_screenshot_1.jpg "Main menu")
![Settings](/screenshots/tashkent_air_bot_screenshot_2.jpg "Settings")

## Features
- **Built with tgbot_template_v3**: The Bot is developed using my `tgbot_template_v3`, ensuring a structured and maintainable codebase.
- **Database Integration**: Utilizes PostgreSQL for data storage, with `SQLAlchemy` for ORM, `asyncpg` for asynchronous database interactions, and `alembic` for database migrations.
- **API Integration**: Fetches air quality data from `aqicin.org` API.
- **Localization**: Implements bot localization using `fluent`, with a custom adapter for seamless integration.
- **Scheduling**: Supports scheduling tasks to send notifications to users.
