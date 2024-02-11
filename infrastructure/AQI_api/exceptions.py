from typing import Union


class ResponseApiError(Exception):
    def __init__(self, response_code: Union[int, str]):
        self.response_code = response_code
        super().__init__(f"Ошибка API. Код ответа: {self.response_code}")


class IncorrectAqiValueApiError(Exception):
    def __init__(self, incorrect_value: Union[int, str]):
        self.incorrect_value = incorrect_value
        super().__init__(f"Некорректное значение: {self.incorrect_value}")


class OutdatedDataApiError(Exception):
    def __init__(self):
        super().__init__("Устаревшие данные.")


class ForecastValueApiError(Exception):
    def __init__(self):
        super().__init__("Отсутствует прогноз на ближайшие дни.")

