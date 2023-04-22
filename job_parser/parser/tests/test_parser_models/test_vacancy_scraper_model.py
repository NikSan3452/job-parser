from parser.models import VacancyScraper

import pytest
from django.forms import ValidationError

TEST_URL = "https://example.com/vacancy/1"
TEST_TITLE = "Test title"
TEST_JOB_BOARD = "JobBoard"
JOB_DESCRIPTION = "JobDescription"
JOB_CITY = "JobCity"
JOB_SALARY = "JobSalary"
JOB_COMPANY = "JobCompany"
JOB_EXPERIENCE = "JobExperience"
JOB_TYPE_OF_WORK = "JobTypeOfWork"
PUBLISHED_AT = "2023-01-01"


@pytest.mark.django_db(transaction=True)
class TestVacancyScraperModelPositive:
    """Класс описывает позитивные тестовые случаи для модели VacancyScraper.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при создании
    объектов модели VacancyScraper: возможность создания объекта модели,
    проверка максимальной длины полей, проверка возможности оставить поле пустым,
    проверка значений по умолчанию и проверка verbose_name полей.
    """

    def test_vacancyscraper_model_creation(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper.

        Создается объект модели VacancyScraper с указанными значениями полей.
        Ожидается, что значения полей будут соответствовать указанным при
        создании объекта.
        """
        vacancy = VacancyScraper.objects.create(
            job_board=TEST_JOB_BOARD,
            url=TEST_URL,
            title=TEST_TITLE,
            description=JOB_DESCRIPTION,
            city=JOB_CITY,
            salary=JOB_SALARY,
            company=JOB_COMPANY,
            experience=JOB_EXPERIENCE,
            type_of_work=JOB_TYPE_OF_WORK,
            remote=True,
            published_at=PUBLISHED_AT,
        )
        assert vacancy.job_board == TEST_JOB_BOARD
        assert vacancy.url == TEST_URL
        assert vacancy.title == TEST_TITLE
        assert vacancy.description == JOB_DESCRIPTION
        assert vacancy.city == JOB_CITY
        assert vacancy.salary == JOB_SALARY
        assert vacancy.company == JOB_COMPANY
        assert vacancy.experience == JOB_EXPERIENCE
        assert vacancy.type_of_work == JOB_TYPE_OF_WORK
        assert vacancy.remote is True
        assert str(vacancy.published_at) == PUBLISHED_AT
        assert str(vacancy) == TEST_TITLE

    def test_vacancyscraper_model_meta(self) -> None:
        """Тест проверяет verbose_name и verbose_name_plural модели VacancyScraper.

        Ожидается, что verbose_name и verbose_name_plural будут соответствовать
        указанным значениям.
        """
        assert VacancyScraper._meta.verbose_name == "Вакансия"
        assert VacancyScraper._meta.verbose_name_plural == "Вакансии"

    def test_job_board_max_length(self) -> None:
        """Тест проверяет максимальную длину поля job_board модели VacancyScraper.

        Ожидается, что максимальная длина поля job_board будет равна 255 символам.
        """
        max_length = VacancyScraper._meta.get_field("job_board").max_length
        assert max_length == 255

    def test_title_max_length(self) -> None:
        """Тест проверяет максимальную длину поля title модели VacancyScraper.

        Ожидается, что максимальная длина поля title будет равна 255 символам.
        """
        max_length = VacancyScraper._meta.get_field("title").max_length
        assert max_length == 255

    def test_city_max_length(self) -> None:
        """Тест проверяет максимальную длину поля city модели VacancyScraper.

        Ожидается, что максимальная длина поля city будет равна 255 символам.
        """
        max_length = VacancyScraper._meta.get_field("city").max_length
        assert max_length == 255

    def test_salary_max_length(self) -> None:
        """Тест проверяет максимальную длину поля salary модели VacancyScraper.

        Ожидается, что максимальная длина поля salary будет равна 255 символам.
        """
        max_length = VacancyScraper._meta.get_field("salary").max_length
        assert max_length == 255

    def test_company_max_length(self) -> None:
        """Тест проверяет максимальную длину поля company модели VacancyScraper.

        Ожидается, что максимальная длина поля company будет равна 255 символам.
        """
        max_length = VacancyScraper._meta.get_field("company").max_length
        assert max_length == 255

    def test_experience_max_length(self) -> None:
        """Тест проверяет максимальную длину поля experience модели VacancyScraper.

        Ожидается, что максимальная длина поля experience будет равна 100 символам.
        """
        max_length = VacancyScraper._meta.get_field("experience").max_length
        assert max_length == 100

    def test_type_of_work_max_length(self) -> None:
        """Тест проверяет максимальную длину поля type_of_work модели VacancyScraper.

        Ожидается, что максимальная длина поля type_of_work будет равна 255 символам.
        """
        VacancyScraper._meta.get_field("type_of_work").max_length

    def test_url_null(self) -> None:
        """Тест проверяет возможность оставить поле url пустым.

        Ожидается, что поле url не может быть пустым.
        """
        null = VacancyScraper._meta.get_field("url").null
        assert null is False

    def test_title_null(self) -> None:
        """Тест проверяет возможность оставить поле title пустым.

        Ожидается, что поле title может быть пустым.
        """
        null = VacancyScraper._meta.get_field("title").null
        assert null is True

    def test_description_null(self) -> None:
        """Тест проверяет возможность оставить поле description пустым.

        Ожидается, что поле description может быть пустым.
        """
        null = VacancyScraper._meta.get_field("description").null
        assert null is True

    def test_city_null(self) -> None:
        """Тест проверяет возможность оставить поле city пустым.

        Ожидается, что поле city может быть пустым.
        """
        null = VacancyScraper._meta.get_field("city").null
        assert null is True

    def test_salary_null(self) -> None:
        """Тест проверяет возможность оставить поле salary пустым.

        Ожидается, что поле salary может быть пустым.
        """
        null = VacancyScraper._meta.get_field("salary").null
        assert null is True

    def test_company_null(self) -> None:
        """Тест проверяет возможность оставить поле company пустым.

        Ожидается, что поле company может быть пустым.
        """
        null = VacancyScraper._meta.get_field("company").null
        assert null is True

    def test_experience_null(self) -> None:
        """Тест проверяет возможность оставить поле experience пустым.

        Ожидается, что поле experience может быть пустым.
        """
        null = VacancyScraper._meta.get_field("experience").null
        assert null is True

    def test_type_of_work_null(self) -> None:
        """Тест проверяет возможность оставить поле type_of_work пустым.

        Ожидается, что поле type_of_work может быть пустым.
        """
        null = VacancyScraper._meta.get_field("type_of_work").null
        assert null is True

    def test_remote_null(self) -> None:
        """Тест проверяет возможность оставить поле remote пустым.

        Ожидается, что поле remote может быть пустым.
        """
        null = VacancyScraper._meta.get_field("remote").null
        assert null is True

    def test_published_at_null(self) -> None:
        """Тест проверяет возможность оставить поле published_at пустым.

        Ожидается, что поле published_at может быть пустым.
        """
        null = VacancyScraper._meta.get_field("published_at").null
        assert null is True

    def test_job_board_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля job_board модели VacancyScraper.

        Ожидается, что verbose_name поля job_board будет равен "Площадка".
        """
        verbose_name = VacancyScraper._meta.get_field("job_board").verbose_name
        assert verbose_name == "Площадка"

    def test_title_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля title модели VacancyScraper.

        Ожидается, что verbose_name поля title будет равен "Вакансия".
        """
        verbose_name = VacancyScraper._meta.get_field("title").verbose_name
        assert verbose_name == "Вакансия"

    def test_description_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля description модели VacancyScraper.

        Ожидается, что verbose_name поля description будет равен "Описание вакансии".
        """
        verbose_name = VacancyScraper._meta.get_field("description").verbose_name
        assert verbose_name == "Описание вакансии"

    def test_city_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля city модели VacancyScraper.

        Ожидается, что verbose_name поля city будет равен "Город".
        """
        verbose_name = VacancyScraper._meta.get_field("city").verbose_name
        assert verbose_name == "Город"

    def test_salary_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля salary модели VacancyScraper.

        Ожидается, что verbose_name поля salary будет равен "Зарплата".
        """
        verbose_name = VacancyScraper._meta.get_field("salary").verbose_name
        assert verbose_name == "Зарплата"

    def test_company_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля company модели VacancyScraper.

        Ожидается, что verbose_name поля company будет равен "Компания".
        """
        verbose_name = VacancyScraper._meta.get_field("company").verbose_name
        assert verbose_name == "Компания"

    def test_experience_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля experience модели VacancyScraper.

        Ожидается, что verbose_name поля experience будет равен "Опыт работы".
        """
        verbose_name = VacancyScraper._meta.get_field("experience").verbose_name
        assert verbose_name == "Опыт работы"

    def test_type_of_work_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля type_of_work модели VacancyScraper.

        Ожидается, что verbose_name поля type_of_work будет равен "Тип занятости".
        """
        verbose_name = VacancyScraper._meta.get_field("type_of_work").verbose_name
        assert verbose_name == "Тип занятости"

    def test_remote_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля remote модели VacancyScraper.

        Ожидается, что verbose_name поля remote будет равен "Удаленная работа".
        """
        verbose_name = VacancyScraper._meta.get_field("remote").verbose_name
        assert verbose_name == "Удаленная работа"

    def test_published_at_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля published_at модели VacancyScraper.

        Ожидается, что verbose_name поля published_at будет равен "Дата публикации".
        """
        verbose_name = VacancyScraper._meta.get_field("published_at").verbose_name
        assert verbose_name == "Дата публикации"

    def test_remote_default(self) -> None:
        """Тест проверяет значение по умолчанию поля remote модели VacancyScraper.

        Ожидается, что значение по умолчанию поля remote будет равно False.
        """
        default = VacancyScraper._meta.get_field("remote").default
        assert default is False


@pytest.mark.django_db(transaction=True)
class TestVacancyScraperModelNegative:
    """Класс описывает негативные тестовые случаи для модели VacancyScraper.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при создании
    объектов модели VacancyScraper: невозможность создания объекта модели без
    обязательных полей, проверка максимальной длины полей и проверка валидации
    значений полей.
    """

    def test_create_vacancyscraper_without_job_board(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper без указания значения
        поля job_board.

        Ожидается, что при попытке создать объект модели VacancyScraper без указания
        значения поля job_board будет вызвано исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(url=TEST_URL)
            vacancy.full_clean()

    def test_create_vacancyscraper_without_url(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper без указания
        значения поля url.

        Ожидается, что при попытке создать объект модели VacancyScraper без указания
        значения поля url будет вызвано исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(job_board=TEST_JOB_BOARD)
            vacancy.full_clean()

    def test_create_vacancyscraper_with_too_long_job_board(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper с указанием
        значения поля job_board превышающего максимальную длину.

        Ожидается, что при попытке создать объект модели VacancyScraper с указанием
        значения поля job_board превышающего максимальную длину будет вызвано
        исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(job_board="a" * 256, url=TEST_URL)
            vacancy.full_clean()

    def test_create_vacancyscraper_with_too_long_title(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper с указанием
        значения поля title превышающего максимальную длину.

        Ожидается, что при попытке создать объект модели VacancyScraper с указанием
        значения поля title превышающего максимальную длину будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(
                job_board=TEST_JOB_BOARD,
                url=TEST_URL,
                title="a" * 256,
            )
            vacancy.full_clean()

    def test_create_vacancyscraper_with_too_long_city(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper с указанием
        значения поля city превышающего максимальную длину.

        Ожидается, что при попытке создать объект модели VacancyScraper с указанием
        значения поля city превышающего максимальную длину будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(
                job_board=TEST_JOB_BOARD,
                url=TEST_URL,
                city="a" * 256,
            )
            vacancy.full_clean()

    def test_create_vacancyscraper_with_too_long_salary(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper с указанием
        значения поля salary превышающего максимальную длину.

        Ожидается, что при попытке создать объект модели VacancyScraper с указанием
        значения поля salary превышающего максимальную длину будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(
                job_board=TEST_JOB_BOARD,
                url=TEST_URL,
                salary="a" * 256,
            )
            vacancy.full_clean()

    def test_create_vacancyscraper_with_too_long_company(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper с указанием значения
        поля company превышающего максимальную длину.

        Ожидается, что при попытке создать объект модели VacancyScraper с указанием
        значения поля company превышающего максимальную длину будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(
                job_board=TEST_JOB_BOARD,
                url=TEST_URL,
                company="a" * 256,
            )
            vacancy.full_clean()

    def test_create_vacancyscraper_with_too_long_experience(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper с указанием значения
        поля experience превышающего максимальную длину.

        Ожидается, что при попытке создать объект модели VacancyScraper с указанием
        значения поля experience превышающего максимальную длину будет вызвано
        исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(
                job_board=TEST_JOB_BOARD,
                url=TEST_URL,
                experience="a" * 101,
            )
            vacancy.full_clean()

    def test_create_vacancyscraper_with_too_long_type_of_work(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper с указанием значения
        поля type_of_work превышающего максимальную длину.

        Ожидается, что при попытке создать объект модели VacancyScraper с указанием
        значения поля type_of_work превышающего максимальную длину будет вызвано
        исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(
                job_board=TEST_JOB_BOARD,
                url=TEST_URL,
                type_of_work="a" * 256,
            )
            vacancy.full_clean()

    def test_create_vacancyscraper_with_invalid_remote(self) -> None:
        """Тест проверяет создание объекта модели VacancyScraper с указанием
        невалидного значения поля remote.

        Ожидается, что при попытке создать объект модели VacancyScraper с указанием
        невалидного значения поля remote будет вызвано исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy = VacancyScraper(
                job_board=TEST_JOB_BOARD,
                url=TEST_URL,
                remote="invalid",
            )
            vacancy.full_clean()
