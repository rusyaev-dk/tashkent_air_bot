from datetime import datetime

from tgbot.services.aqi_scheduler import AQIScheduler

update_aqi_test_cases = [
    {"now": datetime(2024, 12, 5, 14, 3), "expected": datetime(2024, 12, 5, 14, 4, 30)},  # Обычный случай
    {"now": datetime(2024, 12, 5, 14, 59, 50), "expected": datetime(2024, 12, 5, 15, 4, 30)},
    # Переход на следующий час
    {"now": datetime(2024, 12, 31, 23, 58), "expected": datetime(2025, 1, 1, 0, 4, 30)},
    # Переход на следующий день/год
    {"now": datetime(2024, 12, 5, 14, 55), "expected": datetime(2024, 12, 5, 15, 4, 30)},
    # На последнем 5-минутном интервале часа
    {"now": datetime(2024, 12, 5, 14, 0), "expected": datetime(2024, 12, 5, 14, 4, 30)},  # Ровное время

]


notify_user_test_cases = [
    {"now": datetime(2024, 12, 5, 14, 5), "expected": datetime(2024, 12, 5, 15, 0)},  # Обычный случай
    {"now": datetime(2024, 12, 5, 14, 0, 0, 0), "expected": datetime(2024, 12, 5, 15, 0)},  # Ровное время
    {"now": datetime(2024, 12, 5, 23, 59), "expected": datetime(2024, 12, 6, 0, 0)},  # Переход на следующий день
    {"now": datetime(2024, 12, 31, 23, 59), "expected": datetime(2025, 1, 1, 0, 0)},  # Переход на следующий год

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
