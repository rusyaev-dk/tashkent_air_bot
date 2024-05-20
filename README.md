# Tashkent air Telegram Bot

## Features
- **Built with tgbot_template_v3**: The Bot is developed using my `tgbot_template_v3`, ensuring a structured and maintainable codebase.
- **Database Integration**: Utilizes PostgreSQL for data storage, with `SQLAlchemy` for ORM, `asyncpg` for asynchronous database interactions, and `alembic` for database migrations.
- **API Integration**: Fetches air quality data from `aqicin.org` API.
- **Localization**: Implements bot localization using `fluent`, with a custom adapter for seamless integration.
- **Scheduling**: Supports scheduling tasks to send notifications to users.

## Screenshots

<table>
  <tr>
    <td>
      <img src="/screenshots/bot_info.PNG" alt="Bot info" title="Bot info" width="200"/>
    </td>
    <td>
      <img src="/screenshots/hello_screen.PNG" alt="Hello screen" title="Hello screen" width="200"/>
    </td>
     <td>
      <img src="/screenshots/aqi_screen.PNG" alt="AQI screen" title="AQI screen" width="200"/>
    </td>
    <td>
      <img src="/screenshots/informative_screen.PNG" alt="Informative screen" title="Informative screen" width="200"/>
    </td>
  </tr>
  <tr>
    <td>
      <img src="/screenshots/general_settings.PNG" alt="General settings" title="General settings" width="200"/>
    </td>
    <td>
      <img src="/screenshots/notification_settings.PNG" alt="Notification settings" title="Notification settings" width="200"/>
    </td>
    <td>
      <img src="/screenshots/language_settings.PNG" alt="Language settings" title="Language settings" width="200"/>
    </td>
  </tr>
</table>
