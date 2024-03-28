from typing import Union


class ApiResponseCodeException(Exception):
    def __init__(
            self,
            response_code: Union[int, str],
            station_id: str = None
    ):
        self.response_code = response_code
        self.station_id = station_id
        super().__init__(f"ApiResponseCodeException. Bad response from station: {self.station_id}."
                         f"\nResponse code: {self.response_code}")


class ApiNoResponsesException(Exception):
    def __init__(self):
        super().__init__(f"ApiNoResponsesException. No responses.")


class ApiNoDataException(Exception):
    def __init__(self, data_type: Union[int, str]):
        self.data_type = data_type
        super().__init__(f"API Exception. No data type: {self.data_type}.")


class ApiIncorrectKeyException(Exception):
    def __init__(
            self,
            key: str
    ):
        self.key = key
        super().__init__(f"ApiIncorrectKeyException. Incorrect JSON key: {self.key}")


class ApiOutdatedDataException(Exception):
    def __init__(self):
        super().__init__(f"ApiOutdatedDataException. Outdated data.")
