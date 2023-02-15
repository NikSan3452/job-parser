import httpx
import json
from assertions import Assertions

BASE_URL: str = "http://127.0.0.1:8000"

class TestHomePage:
    def test_get_homepage(self) -> None:
        expected_status_code: int = 200

        response = httpx.get(url=BASE_URL)
        Assertions.assert_code_status(response, expected_status_code)


class TestVacancyListPage:

    expected_status_code: int = 200

    def setup_method(self) -> None:
        self.client = httpx.Client()

        response1 = self.client.get(url=BASE_URL)
        self.csrf_token = response1.cookies["csrftoken"]

        data = {
            "login": "user",
            "password": "2x2-XUs-E8W-Pqq",
            "csrfmiddlewaretoken": self.csrf_token,
        }

        response2 = self.client.post(url=f"{BASE_URL}/accounts/login/", data=data)

        self.sessionid = response2.cookies["sessionid"]
        self.auth_csrf = response2.cookies["csrftoken"]
        self.headers = {"X-CSRFToken": self.auth_csrf}

    def test_post_vacancy_list_page(self) -> None:
        data = {
            "job": "Python",
            "city": "Москва",
            "experience": "0",
            "csrfmiddlewaretoken": self.auth_csrf,
        }

        response = self.client.post(url=f"{BASE_URL}/list/", data=data, timeout=20)

        Assertions.assert_code_status(response, self.expected_status_code)

    def test_add_to_favourite(self) -> None:
        data = {
            "url": "https://hh.ru/vacancy/76140465",
            "title": "Python-разработчик",
        }
        data = json.dumps(data)

        self.client.cookies.set("sessionid", self.sessionid)

        response = self.client.post(
            url=f"{BASE_URL}/favourite/", data=data, headers=self.headers
        )

        Assertions.assert_code_status(response, self.expected_status_code)

    def test_delete_favourite(self) -> None:
        data = {
            "url": "https://hh.ru/vacancy/76140465",
        }
        data = json.dumps(data)

        self.client.cookies.set("sessionid", self.sessionid)

        response = self.client.post(
            url=f"{BASE_URL}/delete-favourite/", data=data, headers=self.headers
        )

        Assertions.assert_code_status(response, self.expected_status_code)

    def test_add_to_black_list(self) -> None:
        data = {
            "url": "https://hh.ru/vacancy/76140468",
        }
        data = json.dumps(data)

        self.client.cookies.set("sessionid", self.sessionid)

        response = self.client.post(
            url=f"{BASE_URL}/add-to-black-list/", data=data, headers=self.headers
        )

        Assertions.assert_code_status(response, self.expected_status_code)
