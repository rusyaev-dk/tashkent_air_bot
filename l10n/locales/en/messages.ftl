
hello =
    Hello { $name }!

    ℹ️ To provide and analyze information, we use the Air Quality Index (<b>AQI</b>), which evaluates the level of air pollution based on the concentration of various particles in the atmosphere.

    📑 By using the bot, you automatically accept the { $terms_of_use }.

hello-info = 📌 In the <b>"Settings"</b> section you can change the language and also specify the time at which the bot will send notifications about air quality.

terms-of-use = 📑 By using the bot, you automatically accept the { $terms_of_use }.
terms-of-use-name = user agreement
terms-of-use-link = https://telegra.ph/USER-AGREEMENT-FOR-Tashkent-Air-BOT-12-15

help =
     🛠 If something went wrong, click <b>/start</b> to restart the bot.
     Please report the error to the administration: <b>{ $support_username }</b>

choose-option = ⚙️ Choose option:
main-menu-msg = Main menu:
action-cancelled = Action cancelled.
notifications-enabled = 🔔 Notifications enabled.
notifications-disabled = 🔕 Notifications disabled.
select-notification-time = 🕘 Select a time convenient for you to notify:
settings-applied = ✅ Settings applied

send-feedback = ✉️ Write a message to the administration:
feedback-sent = 📮 Your message has been sent.
reply-from-admin = 💬 Reply from the administrator:

reference =
    🔍 We have collected several useful articles for your reference:

    ❓ { $article_1 }

    ❓ { $article_2 }

    ❓ { $article_3 }

    ❓ { $article_4 }

current-aqi =
    { $pollution_level_emoji } <b>{ $pollution_level }.</b> { $health_implications }

    <b>Air quality index: { $aqi }</b>

    <b>Pollutants (μg/m3):</b>
    - PM2.5: <b>{ $pm25 }</b>
    - PM10: <b>{ $pm10 }</b>
    - o3: <b>{ $o3 }</b>

    ⏳ <b>Updated: { $date } { $month }, { $time }</b>

forecast-aqi-header = <b>Air quality forecast:</b>
forecast-aqi =
    🗓 <b>{ $date } { $month }:</b>
    - PM2.5: <b>{ $pm25_forecast_value }</b>
    - PM10: <b>{ $pm10_forecast_value }</b>
    - o3: <b>{ $o3_forecast_value }</b>
    { $pollution_level_emoji } <b>{ $pollution_level }</b>
