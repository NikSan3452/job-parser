from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """
    Класс конфигурации приложения `profiles`.

    Этот класс наследуется от `AppConfig` и используется для конфигурации 
    приложения profiles`.
    Он содержит атрибуты `default_auto_field` и `name`.    
    Также он содержит метод `ready`, который вызывается при запуске приложения и 
    используется для импорта сигналов из модуля `profiles.signals`.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"

    def ready(self) -> None:
        """
        Метод вызывается при запуске приложения и используется для импорта сигналов
        из модуля `profiles.signals`.

        Returns:
            None
        """
        import profiles.signals
