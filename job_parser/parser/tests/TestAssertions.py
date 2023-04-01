from typing import Any

from django.db import models
from django.db.utils import IntegrityError
from django.http import HttpResponse


class Assertions:
    @staticmethod
    def assert_compare_values(value1: Any, value2: Any) -> None:
        """Сравниевает два значения.

        Args:
            value1 (Any): Значение 1.
            value2 (Any): Значение 2.
        """
        assert value1 == value2, f"Значения {value1} и {value2} не равны"

    @staticmethod
    def assert_type(value: Any, type_: Any) -> None:
        """Проверяет принадлежность к определенному типу.

        Args:
            value1 (Any): Значение
            type_ (Any): Ожидаемый тип.
        """
        if type_ is None:
            assert type_ is None, f"Ожидалось значение None, получили {value}"
        else:
            assert isinstance(
                value, type_
            ), f"Значение {value} не является типом {type_}"

    @staticmethod
    def assert_status_code(response: HttpResponse, expected_status_code: int) -> None:
        """Проверяет код ответа.

        Args:
            response (HttpResponse): Ответ.
            expected_status_code (int): Ожидаемый статус - код.
        """
        assert (
            response.status_code == expected_status_code
        ), f"Неожиданный код ответа, ожидалось {expected_status_code}, получили {response.status_code}"

    @staticmethod
    def assert_value_in_obj(value: Any, obj: Any) -> None:
        """Проверяет вхождение значения в объект.

        Args:
            value (Any): Значение.
            obj (Any): Объект.
        """
        assert value in obj, f"Значение {value} не входит в {obj}"

    @staticmethod
    def assert_value_not_in_obj(value: Any, obj: Any) -> None:
        """Проверяет вхождение значения в объект.

        Args:
            value (Any): Значение.
            obj (Any): Объект.
        """
        assert value not in obj, f"Значение {value} входит в {obj}"

    @staticmethod
    def assert_labels(model: models.Model, field: str, expected: str) -> None:
        """Проверяет имена полей в моделях.

        Args:
            model (models.Model): Объект модели.
            field: (str): Имя поля.
            expected:(str): Ожидаемое значение.
        """
        db_field = model._meta.get_field(field).verbose_name
        assert db_field == expected, f"Поле {db_field} не равно {expected}"

    @staticmethod
    def assert_length(model: models.Model, field: str, expected: int) -> None:
        """Проверяет максимальную длину поля.

        Args:
            model (models.Model): Объект модели.
            field (str): Имя поля.
            expected (int): Ожидаемое значение.
        """
        db_field = model._meta.get_field(field).max_length
        assert db_field == expected, f"Длина поля {field} не равна {expected}"

    @staticmethod
    def assert_unique(model: models.Model, field: str, value: str) -> None:
        """Проверяет на уникальность создаваемый объект.

        Args:
            model (models.Model): Модель.
            field (str): Поле.
            value (str): Значение.
        """
        params = {field: value}
        try:
            model.objects.create(**params)
            assert (
                False
            ), f"Объект с {field}={value} успешно создан, но должен был вызвать IntegrityError"
        except IntegrityError:
            pass  # Ожидаемое исключение, тест прошел успешно

    @staticmethod
    def assert_nullable(model: models.Model, data: dict) -> None:
        """Проверяет, что записываемые данные не являются None.

        Args:
            model (models.Model): Модель.
            data (str): Данные.
        """
        try:
            model.objects.create(**data)
            assert (
                False
            ), f"Объект с {data} успешно записан, но должен был вызвать IntegrityError"
        except IntegrityError:
            pass  # Ожидаемое исключение, тест прошел успешно
