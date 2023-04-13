import datetime
from parser.api.base_parser import Parser
from parser.api.main import run
from parser.api.parsers import Headhunter, SuperJob, Trudvsem

import pytest


async def mock_get_vacancy_from_headhunter(self, url=None, job_board=None) -> dict:
    """Mock-заглушка, имитирует метод получения вакансий из API HeadHunter.

    Args:
        url (_type_, optional): URL-адрес. По-умолчанию None
        job_board (_type_, optional): Площадка. По-умолчанию None.

    Returns:
        dict: Словарь с деталями вакансий.
    """
    mock_job_dict = {
        "title": "Python",
        "job_board": "HeadHunter",
        "published_at": datetime.date(2023, 1, 1),
    }

    # Добавляем значения в главный список с вакансиями.
    Parser.general_job_list.append(mock_job_dict)
    return mock_job_dict


async def mock_get_vacancy_from_superjob(self, url=None, job_board=None) -> dict:
    """Mock-заглушка, имитирует метод получения вакансий из API SuperJob.

    Args:
        url (_type_, optional): URL-адрес. По-умолчанию None
        job_board (_type_, optional): Площадка. По-умолчанию None.

    Returns:
        dict: Словарь с деталями вакансий.
    """
    mock_job_dict = {
        "title": "Python",
        "job_board": "SuperJob",
        "published_at": datetime.date(2023, 1, 1),
    }

    Parser.general_job_list.append(mock_job_dict)
    return mock_job_dict


async def mock_get_vacancy_from_trudvsem(self, url=None, job_board=None) -> dict:
    """Mock-заглушка, имитирует метод получения вакансий из API Trudvsem.

    Args:
        url (_type_, optional): URL-адрес. По-умолчанию None
        job_board (_type_, optional): Площадка. По-умолчанию None.

    Returns:
        dict: Словарь с деталями вакансий.
    """
    mock_job_dict = {
        "title": "Python",
        "job_board": "Trudvsem",
        "published_at": datetime.date(2023, 1, 1),
    }

    Parser.general_job_list.append(mock_job_dict)
    return mock_job_dict


class TestRun:
    """Класс описывает тестовые случаи для функции run."""

    @pytest.mark.asyncio
    async def test_run_only_headhunter(self, mocker) -> None:
        """Тестирует функцию запуска парсера только с площадкой HeadHunter.

        Args:
            mocker (_type_): Фикстура, имитирует результат метода get_vacancy_from_headhunter.
        """
        # Задаем параметры запроса.
        params = {
            "job": "Python",
            "job_board": "HeadHunter",
        }

        # Мокаем метод получения вакансий
        mocker.patch.object(
            Headhunter, "get_vacancy_from_headhunter", mock_get_vacancy_from_headhunter
        )

        # Вызываем парсер
        job_dict = await run(params)

        # Проверяем что полученные значения соответствуют параметрам запроса.
        assert job_dict[0]["title"] == "Python"
        assert job_dict[0]["job_board"] == "HeadHunter"

        Parser.general_job_list.clear()

    @pytest.mark.asyncio
    async def test_run_only_superjob(self, mocker) -> None:
        """Тестирует функцию запуска парсера только с площадкой SuperJob.

        Args:
            mocker (_type_): Фикстура, имитирует результат метода get_vacancy_from_superjob.
        """
        params = {
            "job": "Python",
            "job_board": "SuperJob",
        }

        mocker.patch.object(
            SuperJob, "get_vacancy_from_superjob", mock_get_vacancy_from_superjob
        )

        job_dict = await run(params)

        assert job_dict[0]["title"] == "Python"
        assert job_dict[0]["job_board"] == "SuperJob"

        Parser.general_job_list.clear()

    @pytest.mark.asyncio
    async def test_run_only_trudvsem(self, mocker) -> None:
        """Тестирует функцию запуска парсера только с площадкой Trudvsem.

        Args:
            mocker (_type_): Фикстура, имитирует результат метода get_vacancy_from_trudvsem.
        """
        params = {
            "job": "Python",
            "job_board": "Trudvsem",
        }

        mocker.patch.object(
            Trudvsem, "get_vacancy_from_trudvsem", mock_get_vacancy_from_trudvsem
        )

        job_dict = await run(params)

        assert job_dict[0]["title"] == "Python"
        assert job_dict[0]["job_board"] == "Trudvsem"

        Parser.general_job_list.clear()

    @pytest.mark.asyncio
    async def test_run_all(self, mocker) -> None:
        """Тестирует функцию запуска парсера по всем площадкам.

        Args:
            mocker (_type_): Фикстура, имитирует результат методов получения вакансий.
        """
        params = {
            "job": "Python",
        }

        mocker.patch.object(
            Headhunter, "get_vacancy_from_headhunter", mock_get_vacancy_from_headhunter
        )

        mocker.patch.object(
            SuperJob, "get_vacancy_from_superjob", mock_get_vacancy_from_superjob
        )

        mocker.patch.object(
            Trudvsem, "get_vacancy_from_trudvsem", mock_get_vacancy_from_trudvsem
        )

        job_dict = await run(params)

        assert any(item["job_board"] == "HeadHunter" for item in job_dict)
        assert any(item["job_board"] == "SuperJob" for item in job_dict)
        assert any(item["job_board"] == "Trudvsem" for item in job_dict)
        assert any(item["title"] == "Python" for item in job_dict)

        Parser.general_job_list.clear()
