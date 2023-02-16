from django.http import HttpResponse


class Assertions:
    @staticmethod
    def assert_code_status(response: HttpResponse, expected_status_code: int):
        assert (
            response.status_code == expected_status_code
        ), f"Неожиданный код ответа, ожидалось {expected_status_code}, получили {response.status_code}"

    @staticmethod
    def assert_add_vacancy_to_favorite(vacancy: bool):
        assert vacancy == True, f"Вакансия не была добавлена в избранное"

    @staticmethod
    def assert_delete_vacancy_from_favourite(vacancy: bool):
        assert vacancy == False, f"Вакансия не была удалена из избранного"

    @staticmethod
    def assert_add_vacancy_to_black_list(vacancy: bool):
        assert vacancy == True, f"Вакансия не была добавлена в черный список"
