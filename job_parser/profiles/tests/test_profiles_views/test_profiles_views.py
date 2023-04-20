from typing import Any

import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from profiles.models import Profile


@pytest.fixture
def fix_profile(fix_user: User) -> Profile:
    """Фикстура создающая профиль пользователя.

    Args:
        fix_user (User): Фикстура создающая пользователя.

    Returns:
        Profile: Профиль пользователя.
    """
    profile: Profile = Profile.objects.create(
        user=fix_user, city="Test City", job="Test Job", subscribe=True
    )
    return profile


@pytest.fixture
def logged_in_client(client: Client, fix_user: User) -> Client:
    """Фикстура для предоставления экземпляра пользователя для тестирования.

    Args:
        client (Client): Экземпляр клиента для тестирования.
        test_user (User): Экземпляр пользователя для тестирования.

    Returns:
        Client: Экземпляр клиента с авторизованным пользователем.
    """
    client.force_login(fix_user)
    return client


@pytest.mark.django_db(transaction=True)
class TestProfileView:
    """Класс описывает тестовые случаи для представления ProfileView.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    """

    def test_profile_view_get(
        self, logged_in_client: Client, fix_user: User, fix_profile: Profile
    ) -> None:
        """
        Тест для проверки представления профиля пользователя с методом GET.

        В этом тесте получается URL-адрес для представления профиля пользователя с
        именем пользователя "testuser" и отправляется GET-запрос к этому URL-адресу
        с помощью logged_in_client. Проверяется, что код ответа равен 200 (успешно)
        и что контекст ответа содержит fix_user в качестве пользователя.
        Также проверяется, что начальное значение поля "city" в форме контекста равно
        "Test City".
        Затем отправляется POST-запрос к этому URL-адресу с новыми данными для полей
        "city", "job" и "subscribe". Проверяется, что код ответа равен
        302 (перенаправление) и обновляется профиль из базы данных.
        Проверяется, что значение поля "city" в fix_profile равно "new city", значение
        поля "job" в профиле равно "new job" и значение поля "subscribe" в
        fix_profile равно False.

        Args:
            logged_in_client: Фикстура создающая экземпляр клиента Django,
            с пользователем, который уже вошел в систему
            fix_user: Фикстура создающая экземпляр пользователя
            fix_profile: Фикстура создающая экземпляр профиля пользователя
        """
        # Получение URL представления профиля
        url: str = reverse("profiles:profile", kwargs={"username": "testuser"})

        # Отправка GET-запроса к представлению профиля
        response: HttpResponse = logged_in_client.get(url)

        # Проверка статуса ответа и контекста
        assert response.status_code == 200
        assert response.context["user"] == fix_user
        assert response.context["form"].initial["city"] == "Test City"

        # Отправка POST-запроса с обновленными данными профиля
        response = logged_in_client.post(
            url, data={"city": "New City", "job": "New Job", "subscribe": False}
        )

        # Проверка редиректа и обновления данных профиля
        assert response.status_code == 302
        fix_profile.refresh_from_db()
        assert fix_profile.city == "new city"
        assert fix_profile.job == "new job"
        assert not fix_profile.subscribe

    def test_profile_view_post(
        self, logged_in_client: Client, fix_profile: Profile
    ) -> None:
        """
        Тест для проверки представления профиля пользователя с методом POST.

        В этом тесте получается URL-адрес для представления профиля пользователя с
        именем пользователя "testuser" и отправляется POST-запрос к этому URL-адресу
        с помощью logged_in_client. Проверяется, что код ответа равен 200 (успешно)
        и что контекст ответа содержит fix_user в качестве пользователя.
        Также проверяется, что начальное значение поля "city" в форме контекста равно
        "Test City".
        Затем отправляется POST-запрос к этому URL-адресу с новыми данными для полей
        "city", "job" и "subscribe". Проверяется, что код ответа равен
        302 (перенаправление) и обновляется профиль из базы данных.
        Проверяется, что значение поля "city" в fix_profile равно "new city", значение
        поля "job" в профиле равно "new job" и значение поля "subscribe" в
        fix_profile равно False.
        Также извлекается список сообщений из ответа и проверяется, что он содержит
        только одно сообщение. Проверяется, что текст этого сообщения равен строке
        "Вы отписались от рассылки".

        Args:
            logged_in_client: Фикстура создающая экземпляр клиента Django,
            с пользователем, который уже вошел в систему
            fix_user: Фикстура создающая экземпляр пользователя
            fix_profile: Фикстура создающая экземпляр профиля пользователя
        """
        # Получение URL представления профиля
        url = reverse("profiles:profile", kwargs={"username": "testuser"})

        # Отправка POST-запроса с обновленными данными профиля
        response: HttpResponse = logged_in_client.post(
            url, data={"city": "New City", "job": "New Job", "subscribe": False}
        )

        # Проверка редиректа и обновления данных профиля
        assert response.status_code == 302
        fix_profile.refresh_from_db()
        assert fix_profile.city == "new city"
        assert fix_profile.job == "new job"
        assert not fix_profile.subscribe

        # Проверка сообщений об успехе/ошибке
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Вы отписались от рассылки"

    def test_profile_view_post_invalid_data(
        self, logged_in_client: Client, fix_profile: Profile
    ) -> None:
        """
        Тест для проверки представления профиля пользователя при отправке
        недопустимых данных.

        В этом тесте получается URL-адрес для представления профиля пользователя с
        именем пользователя "testuser" и отправляется POST-запрос к этому URL-адресу
        с помощью logged_in_client с пустыми данными для полей "city" и "job".
        Проверяется, что код ответа равен 200 (успешно) и что форма в контексте ответа
        содержит ошибки для полей "city" и "job".

        Args:
            logged_in_client: Фикстура создающая экземпляр клиента Django,
            с пользователем, который уже вошел в систему
            fix_profile: Фикстура создающая экземпляр профиля пользователя
        """
        # Получение URL представления профиля
        url: str = reverse("profiles:profile", kwargs={"username": "testuser"})

        # Отправка POST-запроса с недопустимыми данными
        response: HttpResponse = logged_in_client.post(
            url, data={"city": "", "job": "", "subscribe": False}
        )

        # Проверка статуса ответа и наличия ошибок в форме
        assert response.status_code == 200
        assert response.context["form"].errors == {
            "city": ["Обязательное поле."],
            "job": ["Обязательное поле."],
        }

    def test_profile_view_not_authenticated(
        self, client: Client, fix_profile: Profile
    ) -> None:
        """
        Тест для проверки представления профиля пользователя при отсутствии
        аутентификации.

        В этом тесте получается URL-адрес для представления профиля пользователя с
        именем пользователя "testuser" и отправляется GET-запрос к этому URL-адресу
        с помощью клиента Django без аутентификации. Проверяется, что код ответа равен
        302 (перенаправление) и что URL-адрес перенаправления содержит URL-адрес для
        входа в систему с параметром "next", равным исходному URL-адресу.

        Args:
            client: Фикстура создающая экземпляр клиента Django
            fix_profile: Фикстура создающая экземпляр профиля пользователя
        """
        # Получение URL представления профиля
        url = reverse("profiles:profile", kwargs={"username": "testuser"})

        # Отправка GET-запроса к представлению профиля без аутентификации
        response: HttpResponse = client.get(url)

        # Проверка редиректа на страницу входа
        assert response.status_code == 302
        assert response.url == f"/accounts/login/?next={url}"

    def test_profile_view_wrong_user(self, client: Client) -> None:
        """
        Тест для проверки представления профиля пользователя при доступе к
        чужому профилю.

        В этом тесте создаются два пользователя с профилями и выполняется вход в систему
        с помощью клиента Django для первого пользователя. Затем получается URL-адрес
        для представления профиля второго пользователя и отправляется GET-запрос к этому
        URL-адресу. Проверяется, что код ответа равен 403 (запрещено).

        Args:
            client: Фикстура создающая экземпляр клиента Django
        """
        # Создание двух пользователей и профилей
        user1 = User.objects.create_user(username="testuser1", password="testpass")
        Profile.objects.create(
            user=user1, city="Test City 1", job="Test Job 1", subscribe=True
        )
        user2 = User.objects.create_user(username="testuser2", password="testpass")
        Profile.objects.create(
            user=user2, city="Test City 2", job="Test Job 2", subscribe=True
        )

        # Аутентификация первого пользователя
        client.login(username="testuser1", password="testpass")

        # Получение URL представления профиля второго пользователя
        url = reverse("profiles:profile", kwargs={"username": "testuser2"})

        # Отправка GET-запроса к представлению профиля второго пользователя
        response: HttpResponse = client.get(url)

        # Проверка статуса ответа
        assert response.status_code == 403

    def test_get_initial_with_exception(
        self, logged_in_client: Client, fix_profile: Profile, fix_user: User, mocker
    ) -> None:
        """
        Тест для проверки исключения при получении начальных данных формы профиля.

        В этом тесте используется mocker для имитации исключения ObjectDoesNotExist при
        вызове метода get у менеджера модели Profile. Затем отправляется GET-запрос к
        URL-адресу представления профиля пользователя с помощью logged_in_client и
        проверяется, что вызывается исключение ObjectDoesNotExist.

        Args:
            logged_in_client: Фикстура создающая экземпляр клиента Django,
            с пользователем, который уже вошел в систему
            fix_profile: Фикстура создающая экземпляр профиля пользователя
            fix_user: Фикстура создающая экземпляр пользователя
            mocker: Фикстура для имитации поведения объектов
        """
        url = reverse("profiles:profile", kwargs={"username": fix_user.username})

        # Проверка исключения ObjectDoesNotExist
        mocker.patch(
            "profiles.models.Profile.objects.get", side_effect=ObjectDoesNotExist
        )
        with pytest.raises(ObjectDoesNotExist):
            logged_in_client.get(url)

    def test_get_context_data_with_exception(
        self,
        logged_in_client: Client,
        fix_profile: Profile,
        fix_user: User,
        mocker: Any,
    ) -> None:
        """
        Тест для проверки исключения при получении контекста данных представления
        профиля.

        В этом тесте используется mocker для имитации исключения ObjectDoesNotExist при
        вызове метода filter у менеджера модели FavouriteVacancy. Затем отправляется
        GET-запрос к URL-адресу представления профиля пользователя с помощью
        logged_in_client и проверяется, что вызывается исключение ObjectDoesNotExist.

        Args:
            logged_in_client: Фикстура создающая экземпляр клиента Django,
            с пользователем, который уже вошел в систему
            fix_profile: Фикстура создающая экземпляр профиля пользователя
            fix_user: Фикстура создающая экземпляр пользователя
            mocker: Фикстура для имитации поведения объектов
        """
        url = reverse("profiles:profile", kwargs={"username": fix_user.username})

        # Проверка исключения ObjectDoesNotExist
        mocker.patch(
            "parser.models.FavouriteVacancy.objects.filter",
            side_effect=ObjectDoesNotExist,
        )
        with pytest.raises(ObjectDoesNotExist):
            logged_in_client.get(url)

    def test_form_valid_with_exception(
        self,
        logged_in_client: Client,
        fix_profile: Profile,
        fix_user: User,
        mocker: Any,
    ) -> None:
        """
        Тест для проверки исключения при проверке валидности формы профиля.

        В этом тесте используется mocker для имитации исключения ObjectDoesNotExist при
        вызове метода get у менеджера модели Profile. Затем отправляется POST-запрос к
        URL-адресу представления профиля пользователя с помощью logged_in_client с
        данными для полей "city", "job" и "subscribe" и проверяется, что вызывается
        исключение ObjectDoesNotExist.

        Args:
            logged_in_client: Фикстура создающая экземпляр клиента Django,
            с пользователем, который уже вошел в систему
            fix_profile: Фикстура создающая экземпляр профиля пользователя
            fix_user: Фикстура создающая экземпляр пользователя
            mocker: Фикстура для имитации поведения объектов
        """
        url = reverse("profiles:profile", kwargs={"username": fix_user.username})

        # Проверка исключения ObjectDoesNotExist
        mocker.patch(
            "profiles.models.Profile.objects.get", side_effect=ObjectDoesNotExist
        )
        with pytest.raises(ObjectDoesNotExist):
            logged_in_client.post(
                url,
                data={"city": "test city", "job": "test job", "subscribe": True},
            )
