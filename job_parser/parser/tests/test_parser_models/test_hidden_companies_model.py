import pytest
from django.contrib.auth.models import User
from parser.models import HiddenCompanies

from parser.tests.TestAssertions import Assertions


@pytest.mark.django_db
class TestHiddenCompaniesModel:
    """Тестовый случай для модели HiddenCompanies приложения parser."""

    def setup_data(self, test_user: User) -> tuple[HiddenCompanies, dict]:
        """Устанавливает тестовые данные для модели HiddenCompanies.
        Args:
            test_user (User): Тестовый пользователь.
        Returns:
            tuple[HiddenCompanies, dict]: Словарь с тестовыми данными и объект модели.
        """
        data = dict(
            user=test_user,
            name="test_name",
        )

        HiddenCompanies.objects.create(**data)
        db_obj = HiddenCompanies.objects.get(name=data.get("name", ""))

        return db_obj, data

    def test_vacancy_black_list_labels(self, test_user: User) -> None:
        """Тестирует текстовые метки модели HiddenCompanies."""
        data = self.setup_data(test_user)

        Assertions.assert_labels(data[0], "user", "Пользователь")
        Assertions.assert_labels(data[0], "name", "Компания")
        Assertions.assert_length(HiddenCompanies, "name", 255)
