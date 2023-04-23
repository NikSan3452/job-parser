from allauth.account.signals import user_signed_up
from django.contrib.auth.models import User
from django.dispatch import receiver
from logger import logger, setup_logging

from .models import Profile

# Логирование
setup_logging()


@receiver(user_signed_up, sender=User)
def create_profile(sender: User, **kwargs) -> Profile:
    """
    Функция-обработчик сигнала `user_signed_up`.

    Эта функция вызывается после регистрации пользователя и используется для создания 
    профиля пользователя.
    Она принимает отправителя сигнала `sender` и дополнительные аргументы `kwargs`.
    Внутри функции извлекается пользователь из аргументов и пытается создать профиль 
    пользователя с помощью метода `get_or_create` модели `Profile`.
    Если профиль был успешно создан, в лог записывается информация об этом.
    В случае возникновения исключения оно записывается в лог.
    В конце функции возвращается созданный профиль.

    Args:
        sender (User): Отправитель сигнала.
        kwargs (dict): Дополнительные аргументы.

    Returns:
        Profile: Созданный профиль пользователя.
    """
    user = kwargs["user"]
    try:
        profile = Profile.objects.get_or_create(user=user)
        logger.debug(f"Создан профиль {user}")
    except Exception as exc:
        logger.exception(exc)
    return profile
