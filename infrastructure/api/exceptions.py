from typing import Union


class ApiException(Exception):
    def __init__(
            self,
            msg: str,
            response_code: Union[int, str],
    ):
        self.response_code = response_code
        self.msg = msg
        super().__init__(msg, response_code)

    def what(self):
        return f"ApiException. Response code: {self.response_code}. Message: {self.msg}"
