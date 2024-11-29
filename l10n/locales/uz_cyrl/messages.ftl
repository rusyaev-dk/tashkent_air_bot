hello =
    Салом, { $name }!

    ℹ️ Ахборотни тақдим этиш ва таҳлил қилиш учун биз атмосферадаги турли заррачалар концентрацияси асосида ҳавонинг ифлосланиш даражасини баҳоловчи Ҳаво сифати индексига (<b>AQI</b>) таянамиз.

    📑 Ботдан фойдаланиш орқали сиз { $terms_of_use } автоматик равишда қабул қиласиз.

hello-info = 📌 <b>«Созламалар»</b> бўлимида сиз тилни ўзгартиришингиз, шунингдек, бот ҳаво сифати ҳақида билдиришнома юбориш вақтини белгилашингиз мумкин.

terms-of-use = 📑 Ботдан фойдаланиш орқали сиз { $terms_of_use } автоматик равишда қабул қиласиз.
terms-of-use-name = фойдаланувчи шартномасини
terms-of-use-link = https://telegra.ph/Toshkent-Air-BOT-UCHUN-FOYDALANUVCHI-SHARTNOMASI-02-01

help =
     🛠 Агар бирор нарса нотўғри бўлса, ботни қайта ишга тушириш учун <b>/start</b> тугмасини босинг.
     Хато ҳақида маъмуриятга хабар беринг: <b>{ $support_username }</b>

choose-option = ⚙️ Вариантни танланг:
main-menu-msg = Асосий меню:
action-cancelled = Амал бекор қилинди.
notifications-enabled = 🔔 Билдиришномалар ёқилди.
notifications-disabled = 🔕 Билдиришномалар ўчирилди.
choose-notification-time = 🕘 Хабар бериш учун қулай вақтни танланг:
settings-applied = ✅ Созламалар қўлланилди

send-feedback = ✉️ Маъмуриятга хабар ёзинг:
feedback-sent = 📮 Хабарингиз жўнатилди.
reply-from-admin = 💬 Администратордан жавоб:

reference =
    🔍 Маълумот учун биз бир нечта фойдали мақолаларни тўпладик:

    ❓ { $article_1 }

    ❓ { $article_2 }

    ❓ { $article_3 }

    ❓ { $article_4 }

current-aqi =
    { $pollution_level_emoji } <b>{ $pollution_level }.</b> { $health_implications }

    <b>Ҳаво сифати индекси: { $aqi } </b>

    <b>Ифлослантирувчи моддалар (μg/m3):</b>
    - PM2.5: <b>{ $pm25 }</b>
    - PM10: <b>{ $pm10 }</b>
    - o3: <b>{ $o3 }</b>

    ⏳ <b>Янгиланди: { $date } { $month }, { $time }</b>

forecast-aqi-header = <b>Ҳаво сифати прогнози:</b>
forecast-aqi =
    🗓 <b>{ $date } { $month }:</b>
    - PM2.5: <b>{ $pm25_forecast_value }</b>
    - PM10: <b>{ $pm10_forecast_value }</b>
    - o3: <b>{ $o3_forecast_value }</b>
    { $pollution_level_emoji } <b>{ $pollution_level }</b>
