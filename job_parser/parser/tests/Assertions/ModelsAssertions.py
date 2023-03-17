from django.db import models
from django.db.utils import IntegrityError


class ModelsAssertions:
    @staticmethod
    def assert_labels(obj: models.Model, field: str, expected: str) -> None:
        """Проверяет имена полей в моделях.

        Args:
            obj (models.Model): Объект модели.
            field: (str): Имя поля.
            expected:(str): Ожидаемое значение.
        """
        db_field = obj._meta.get_field(field).verbose_name
        assert db_field == expected, f"Поле {db_field} не равно {expected}"

    @staticmethod
    def assert_length(obj: models.Model, field: str, expected: str) -> None:
        """Проверяет максимальную длину поля.

        Args:
            obj (models.Model): Объект модели.
            field (str): Имя поля.
            expected (str): Ожидаемое значение.
        """
        db_field = obj._meta.get_field(field).max_length
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
            