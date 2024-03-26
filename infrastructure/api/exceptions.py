from typing import Union


class ApiResponseCodeException(Exception):
    def __init__(self, response_code: Union[int, str], traceback: str):
        self.response_code = response_code
        super().__init__(f"API Exception. Response code: {self.response_code}. Traceback: {traceback}")


class ApiNoResponsesException(Exception):
    def __init__(self, traceback: str):
        super().__init__(f"API Exception. No responses. Traceback: {traceback}")


class ApiIncorrectValueException(Exception):
    def __init__(self, incorrect_value: Union[int, str]):
        self.incorrect_value = incorrect_value
        super().__init__(f"API Exception. Incorrect aqi value: {self.incorrect_value}")


class OutdatedDataApiError(Exception):
    def __init__(self):
        super().__init__("Устаревшие данные.")


class ForecastValueApiError(Exception):
    def __init__(self):
        super().__init__("Отсутствует прогноз на ближайшие дни.")

