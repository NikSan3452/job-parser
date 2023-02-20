import datetime
from django.http import HttpResponse


class Assertions:
    @staticmethod
    def assert_code_status(response: HttpResponse, expected_status_code: int) -> None:
        """Проверяет код ответа.

        Args:
            response (HttpResponse): Ответ.
            expected_status_code (int): Ожидаемый статус - код.
        """
        assert (
            response.status_code == expected_status_code
        ), f"Неожиданный код ответа, ожидалось {expected_status_code}, получили {response.status_code}"

    @staticmethod
    def assert_add_vacancy_to_favorite(vacancy_exists: bool) -> None:
        """Проверяет добавлена ли вакансия в избранное.

        Args:
            vacancy_exists (bool): True/False.
        """
        assert vacancy_exists == True, f"Вакансия не была добавлена в избранное"

    @staticmethod
    def assert_delete_vacancy_from_favourite(vacancy_exists: bool) -> None:
        """Проверяет удалена ли вакансия из избранного.

        Args:
            vacancy_exists (bool): True/False.
        """
        assert vacancy_exists == False, f"Вакансия не была удалена из избранного"

    @staticmethod
    def assert_add_vacancy_to_black_list(vacancy_exists: bool) -> None:
        """Проверяет добавлена ли вакансия в черный список.

        Args:
            vacancy_exists (bool): True/False.
        """
        assert vacancy_exists == True, f"Вакансия не была добавлена в черный список"

    @staticmethod
    def assert_object_in_response_context(obj: str, response: HttpResponse) -> None:
        """Проверяет находится ли объект в контексте ответа.

        Args:
            obj (str): Объект.
            response (HttpResponse): True/False
        """
        assert obj in response.context, f"{obj} не существует в контексте ответа"

    @staticmethod
    def assert_compare_obj_and_response_obj(
        obj: str, name: str, response: HttpResponse
    ) -> None:
        """Сравнивает значения передаваемых параметров со значениями из контекста.

        Args:
            obj (str): Объект.
            name (str): Имя объекта.
            response (HttpResponse): Ответ.
        """
        if obj is None:
            obj = ""
        if response.context[0][name] is None:
            response.context[0][name] = ""
        if isinstance(response.context[0][name], datetime.date):
            response.context[0][name] = datetime.date.strftime(
                response.context[0][name], "%Y-%m-%d"
            )
        if isinstance(response.context[0][name], int):
            response.context[0][name] = str(response.context[0][name])
        if isinstance(response.context[0][name], bool):
            response.context[0][name] = str(response.context[0][name])
        if isinstance(obj, bool):
            obj = str(obj)

        assert (
            obj.lower() == response.context[0][name].lower()
        ), f"{obj} не равно {response.context[0][name]}"
