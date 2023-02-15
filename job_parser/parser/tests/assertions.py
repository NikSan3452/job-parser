import httpx


class Assertions:
    @staticmethod
    def assert_code_status(response: httpx.Response, expected_status_code: int):
        assert (
            response.status_code == expected_status_code
        ), f"Неожиданный код ответа, ожидалось {expected_status_code}, получили {response.status_code}"
