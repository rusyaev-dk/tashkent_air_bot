from datetime import datetime

from tgbot.services.aqi_scheduler import AQIScheduler

update_aqi_test_cases = [
    # Стандартные случаи
    {"now": datetime(2024, 12, 5, 8, 35), "expected": datetime(2024, 12, 5, 8, 40)},  # Ближайший 10-минутный интервал
    {"now": datetime(2024, 12, 5, 8, 59), "expected": datetime(2024, 12, 5, 9, 0)},  # Переход на следующий час
    {"now": datetime(2024, 12, 5, 23, 55), "expected": datetime(2024, 12, 6, 0, 0)},  # Переход на следующий день
    {"now": datetime(2024, 12, 5, 0, 0), "expected": datetime(2024, 12, 5, 0, 10)},  # В начале суток
    {"now": datetime(2024, 12, 5, 11, 0), "expected": datetime(2024, 12, 5, 11, 10)},  # Начало часа

    # Краевые случаи
    {"now": datetime(2024, 12, 31, 23, 59), "expected": datetime(2025, 1, 1, 0, 0)},  # Новый год
    {"now": datetime(2024, 2, 29, 23, 59), "expected": datetime(2024, 3, 1, 0, 0)},  # Високосный год
    {"now": datetime(2024, 12, 5, 8, 50), "expected": datetime(2024, 12, 5, 9, 0)},  # Почти следующий час
    {"now": datetime(2024, 12, 5, 8, 0), "expected": datetime(2024, 12, 5, 8, 10)},  # Точно начало часа
    {"now": datetime(2024, 12, 5, 8, 9), "expected": datetime(2024, 12, 5, 8, 10)},  # Первая минута

    # Пограничные случаи
    {"now": datetime(2024, 12, 5, 23, 0), "expected": datetime(2024, 12, 5, 23, 10)},  # Последний час
    {"now": datetime(2024, 12, 5, 22, 59), "expected": datetime(2024, 12, 5, 23, 0)},  # Последняя минута перед часом
    {"now": datetime(2024, 12, 5, 7, 59), "expected": datetime(2024, 12, 5, 8, 0)},  # Минуты до следующего часа
    {"now": datetime(2024, 12, 5, 23, 30), "expected": datetime(2024, 12, 5, 23, 40)},  # Половина часа
    {"now": datetime(2024, 12, 5, 15, 25), "expected": datetime(2024, 12, 5, 15, 30)},  # Середина часа

    # Редкие случаи
    {"now": datetime(2024, 12, 5, 15, 1), "expected": datetime(2024, 12, 5, 15, 10)},  # Первая минута после часа
    {"now": datetime(2024, 12, 5, 14, 45), "expected": datetime(2024, 12, 5, 14, 50)},  # Почти конец часа
    {"now": datetime(2024, 12, 5, 0, 1), "expected": datetime(2024, 12, 5, 0, 10)},  # Сразу после полуночи
    {"now": datetime(2024, 12, 5, 13, 59), "expected": datetime(2024, 12, 5, 14, 0)},  # Середина дня
    {"now": datetime(2024, 12, 5, 12, 0), "expected": datetime(2024, 12, 5, 12, 10)},  # Ровно в полдень
]


notify_user_test_cases = [
    {"now": datetime(2024, 12, 5, 14, 30), "expected": datetime(2024, 12, 5, 14, 59)},  # 14:30 -> 14:59
    {"now": datetime(2024, 12, 5, 14, 58), "expected": datetime(2024, 12, 5, 14, 59)},  # 14:58 -> 14:59
    {"now": datetime(2024, 12, 5, 14, 59), "expected": datetime(2024, 12, 5, 14, 59)},  # 14:59 -> 14:59
    {"now": datetime(2024, 12, 5, 15, 0), "expected": datetime(2024, 12, 5, 15, 59)},  # 15:00 -> 15:59
    {"now": datetime(2024, 12, 5, 23, 50), "expected": datetime(2024, 12, 5, 23, 59)},  # 23:50 -> 23:59
    {"now": datetime(2024, 12, 5, 23, 58), "expected": datetime(2024, 12, 5, 23, 59)},  # 23:58 -> 23:59
    {"now": datetime(2024, 12, 5, 23, 59), "expected": datetime(2024, 12, 5, 23, 59)},  # 23:59 -> 23:59
    {"now": datetime(2024, 12, 6, 0, 0), "expected": datetime(2024, 12, 6, 0, 59)},  # 00:00 -> 00:59
    {"now": datetime(2024, 12, 6, 0, 30), "expected": datetime(2024, 12, 6, 0, 59)},  # 00:30 -> 00:59
    {"now": datetime(2024, 12, 6, 1, 10), "expected": datetime(2024, 12, 6, 1, 59)},  # 01:10 -> 01:59
    # Переход на новый день
    {"now": datetime(2024, 12, 31, 23, 50), "expected": datetime(2024, 12, 31, 23, 59)},  # 23:50 -> 23:59
    {"now": datetime(2024, 12, 31, 23, 58), "expected": datetime(2024, 12, 31, 23, 59)},  # 23:58 -> 23:59
    {"now": datetime(2024, 12, 31, 23, 59), "expected": datetime(2024, 12, 31, 23, 59)},  # 23:59 -> 23:59
    {"now": datetime(2025, 1, 1, 0, 0), "expected": datetime(2025, 1, 1, 0, 59)},  # Новый год: 00:00 -> 00:59
    {"now": datetime(2025, 1, 1, 0, 30), "expected": datetime(2025, 1, 1, 0, 59)},  # Новый год: 00:30 -> 00:59
    {"now": datetime(2025, 1, 1, 1, 10), "expected": datetime(2025, 1, 1, 1, 59)},  # Новый год: 01:10 -> 01:59
    # Переход на новый день в новый год
    {"now": datetime(2025, 1, 1, 0, 0), "expected": datetime(2025, 1, 1, 0, 59)},  # Новый год: 00:00 -> 00:59
    {"now": datetime(2025, 1, 1, 0, 59), "expected": datetime(2025, 1, 1, 0, 59)},  # Новый год: 00:59 -> 00:59
    {"now": datetime(2025, 1, 1, 23, 59), "expected": datetime(2025, 1, 1, 23, 59)},  # 23:59 -> 23:59 (новый день)
]

if __name__ == "__main__":
    for i, test_case in enumerate(update_aqi_test_cases, start=1):
        result = AQIScheduler.get_update_first_run_time(test_case["now"])
        print(f"Test {i}: Now = {test_case['now']}, Expected = {test_case['expected']}, Result = {result}")
        assert result == test_case["expected"], f"Test {i} failed: {result} != {test_case['expected']}"

    for i, test_case in enumerate(notify_user_test_cases, start=1):
        result = AQIScheduler.get_notify_first_run_time(test_case["now"])
        print(f"Test {i}: Now = {test_case['now']}, Expected = {test_case['expected']}, Result = {result}")
        assert result == test_case["expected"], f"Test {i} failed: {result} != {test_case['expected']}"
