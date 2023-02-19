import pytest

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from profiles.models import Profile


@pytest.mark.django_db
class TestProfile:
    client: Client = Client()

    def setup_method(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="testuser@example.com"
        )
        self.client.force_login(user=self.user)

    def test_profile_view_method_get(self) -> None:
        """Тестирует страницу профиля."""
        response = self.client.get(reverse("profiles:profile", args=[self.user.username]))

        assert response.status_code == 200

    def test_profile_view_method_post(self) -> None:
        """Тестирует подписку на рассылку вакансий.

        Args:
            client (Client): Клиент.
        """

        data = {
            "city": "Москва",
            "job": "Backend-разработчик",
            "subscribe": True,
        }

        response = self.client.post(
            reverse("profiles:profile", args=[self.user.username]), data=data
        )

        assert response.status_code == 302

        profile = Profile.objects.get(user=self.user)

        assert profile.city == "Москва".lower()
        assert profile.job == "Backend-разработчик".lower()
        assert profile.subscribe == True
