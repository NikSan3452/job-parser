from parser.forms import SearchingForm

import pytest


class TestProfileForm:
    @pytest.mark.parametrize(
        "job, city, subscribe, validity",
        [
            ("Python", "Москва", False, True),
            ("Python", "Москва", True, True),
        ],
    )
    def test_valid_searching_form(
        self,
        job: str,
        city: str,
        subscribe: str,
        validity: bool,
    ) -> None:
        """
        Тест проверяет валидность формы поиска.

        Этот метод принимает строку с названием работы `job`, строку с названием
        города `city`, логическое значение подписки `subscribe` и логическое значение
        валидности `validity`.
        Внутри метода создается экземпляр формы `SearchingForm` с данными из параметров.
        Затем проверяется валидность формы и сравнивается с ожидаемым значением.

        Args:
            job (str): Название работы.
            city (str): Название города.
            subscribe (str): Значение подписки.
            validity (bool): Ожидаемое значение валидности формы.

        Returns:
            None
        """
        form = SearchingForm(
            data={
                "job": job,
                "city": city,
                "subscribe": subscribe,
            }
        )

        assert form.is_valid() is validity
        assert form.is_valid() is validity
