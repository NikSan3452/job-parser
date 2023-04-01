from parser.models import FavouriteVacancy
from parser.tests.TestAssertions import Assertions

import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db(transaction=True)
class TestFavouriteVacancyModel:
    def setup_data(self, test_user: User) -> tuple[FavouriteVacancy, dict]:
        """Устанавливает тестовые данные.
        Args:
            test_user (User): Тестовый пользователь.
        Returns:
            tuple[FavouriteVacancy, dict]: Словарь с тестовыми данными и объект модели.
        """
        data = dict(
            user=test_user,
            url="http://test_url.com",
            title="test_title",
        )
        FavouriteVacancy.objects.create(**data)
        db_obj = FavouriteVacancy.objects.get(url=data.get("url", ""))
        return db_obj, data

    def test_favourite_vacancy_labels(self, test_user: User) -> None:
        """Тестирует текстовые метки модели FavouriteVacancy."""
        data = self.setup_data(test_user)

        Assertions.assert_labels(data[0], "user", "Пользователь")
        Assertions.assert_labels(data[0], "title", "Вакансия")
        Assertions.assert_unique(FavouriteVacancy, "url", "http://test_url.com")
        Assertions.assert_nullable(FavouriteVacancy, data[1])
        Assertions.assert_length(FavouriteVacancy, "title", 250)
