
hello =
    Здравствуйте, { $name }!

    ℹ️ Для выдачи и анализа информации мы используем индекс качества воздуха (<b>AQI</b>), который оценивает уровень загрязнения воздуха на основе концентрации различных частиц в атмосфере.

    📑 Пользуясь ботом, Вы автоматически принимаете { $terms_of_use }.

hello-info = 📌 В разделе <b>«Настройки»</b> Вы можете сменить язык, а также указать время, в которое бот будет присылать уведомления о качестве воздуха.

terms-of-use = 📑 Пользуясь ботом, Вы автоматически принимаете { $terms_of_use }.
terms-of-use-name = пользовательское соглашение
terms-of-use-link = https://telegra.ph/POLZOVATELSKOE-SOGLASHENIE-DLYA-BOTA-Tashkent-Air-01-31-2

help =
    🛠 Если что-то пошло не так, нажмите <b>/start</b>, чтобы перезапустить бота.
    Пожалуйста, сообщите об ошибке администрации: <b>{ $support_username }</b>

choose-option = ⚙️ Выберите опцию:
main-menu = Главное меню:
action-cancelled = Действие отменено.
notifications-enabled = 🔔 Уведомления включены.
notifications-disabled = 🔕 Уведомления выключены.
choose-notification-time = 🕘 Выберите удобное Вам время для уведомления:
settings-applied = ✅ Настройки применены

send-feedback = ✉️ Напишите сообщение администрации:
feedback-sent = 📮 Ваше сообщение отправлено.
reply-from-admin = 💬 Ответ от администратора:

reference =
    🔍 Мы собрали несколько полезных статей для ознакомления:

    ❓ { $article_1 }

    ❓ { $article_2 }

    ❓ { $article_3 }

    ❓ { $article_4 }

current-aqi =
    { $pollution_level_emoji } <b>{ $pollution_level }.</b> { $health_implications }

    <b>Индекс качества воздуха:</b>
    - PM2.5: <b>{ $pm25_value }</b>
    - PM10: <b>{ $pm10_value }</b>
    - o3: <b>{ $o3_value }</b>

    ⏳ <b>Обновлено: { $date } { $month }, { $time }</b>

forecast-aqi-header = <b>Прогноз качества воздуха:</b>
forecast-aqi =
    🗓 <b>{ $date } { $month }</b>:
    - PM2.5: <b>{ $pm25_forecast_value }</b>
    - PM10: <b>{ $pm10_forecast_value }</b>
    - o3: <b>{ $o3_forecast_value }</b>
    { $pollution_level_emoji } <b>{ $pollution_level }</b>
