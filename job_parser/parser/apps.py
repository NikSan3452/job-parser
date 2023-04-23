from django.apps import AppConfig


class ParserConfig(AppConfig):
    """
    Класс конфигурации приложения `parser`.

    Этот класс наследуется от `AppConfig` и используется для конфигурации приложения 
    `parser`.
    Он содержит атрибуты `default_auto_field` и `name`.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "parser"
