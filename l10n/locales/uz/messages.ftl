
hello =
    Assalomu alaykum, { $name }!

    ℹ️ Axborotni taqdim etish va tahlil qilish uchun biz atmosferadagi turli zarrachalar kontsentratsiyasi asosida havoning ifloslanish darajasini baholaydigan Havo sifati indeksidan (<b>AQI</b>) foydalanamiz.

    📑 Botdan foydalanish orqali siz { $terms_of_use} avtomatik ravishda qabul qilasiz.

hello-info = 📌 <b>«Sozlamalar»</b> bo'limida siz tilni o'zgartirishingiz, shuningdek, bot havo sifati haqida bildirishnoma yuborish vaqtini belgilashingiz mumkin.

terms-of-use = 📑 Botdan foydalanish orqali siz { $terms_of_use} avtomatik ravishda qabul qilasiz.
terms-of-use-name = foydalanuvchi shartnomasini
terms-of-use-link = https://telegra.ph/Toshkent-Air-BOT-UCHUN-FOYDALANUVCHI-SHARTNOMASI-12-15

help =
     🛠 Agar biror narsa noto'g'ri bo'lsa, botni qayta ishga tushirish uchun <b>/start</b> tugmasini bosing.
     Xato haqida ma'muriyatga xabar bering: <b>{ $support_username }</b>

choose-option = ⚙️ Variantni tanlang:
main-menu-msg = Asosiy menyu:
action-cancelled = Amal bekor qilindi.
notifications-enabled = 🔔 Bildirishnomalar yoqilgan.
notifications-disabled = 🔕 Bildirishnomalar o'chirilgan.
select-notification-time = 🕘 Xabar berish uchun qulay vaqtni tanlang:
settings-applied = ✅ Sozlamalar qoʻllanildi

send-feedback = ✉️ Ma'muriyatga xabar yozing:
feedback-sent = 📮 Xabaringiz jo'natildi.
reply-from-admin = 💬 Administratordan javob:

reference =
    🔍 Malumot uchun biz bir nechta foydali maqolalarni to'pladik:

    ❓ { $article_1 }

    ❓ { $article_2 }

    ❓ { $article_3 }

    ❓ { $article_4 }

current-aqi =
    { $pollution_level_emoji } <b>{ $pollution_level }.</b> { $health_implications }

    <b>Havo sifati indeksi: { $aqi } </b>

    <b>Ifloslantiruvchi moddalar (μg/m3):</b>
    - PM2.5: <b>{ $pm25 }</b>
    - PM10: <b>{ $pm10 }</b>
    - o3: <b>{ $o3 }</b>

    ⏳ <b>Yangilangan: { $date } { $month }, { $time }</b>

forecast-aqi-header = <b>Havo sifati prognozi:</b>
forecast-aqi =
    🗓 <b>{ $date } { $month }:</b>
    - PM2.5: <b>{ $pm25_forecast_value }</b>
    - PM10: <b>{ $pm10_forecast_value }</b>
    - o3: <b>{ $o3_forecast_value }</b>
    { $pollution_level_emoji } <b>{ $pollution_level }</b>
