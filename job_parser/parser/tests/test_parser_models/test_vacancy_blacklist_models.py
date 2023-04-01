from parser.models import VacancyBlackList
from parser.tests.TestAssertions import Assertions

import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db(transaction=True)
class TestVacancyBlackListModel:
    """Тестовый случай для модели VacancyBlackList приложения parser."""

    def setup_data(self, test_user: User) -> tuple[VacancyBlackList, dict]:
        """Устанавливает тестовые данные для модели VacancyBlackList.

        Args:
            test_user (User): Тестовый пользователь.

        Returns:
            tuple[VacancyBlackList, dict]: Словарь с тестовыми данными и объект модели.
        """
        data = dict(
            user=test_user,
            url="http://test_url.com",
            title="test_title",
        )
        VacancyBlackList.objects.create(**data)
        db_obj = VacancyBlackList.objects.get(url=data.get("url", ""))
        return db_obj, data

    def test_vacancy_black_list_labels(self, test_user: User) -> None:
        """Тестирует текстовые метки модели VacancyBlackList."""
        data = self.setup_data(test_user)

        Assertions.assert_labels(data[0], "user", "Пользователь")
        Assertions.assert_labels(data[0], "title", "Вакансия")
        Assertions.assert_unique(VacancyBlackList, "url", "http://test_url.com")
        Assertions.assert_nullable(VacancyBlackList, data[1])
        Assertions.assert_length(VacancyBlackList, "title", 250)
