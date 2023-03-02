from allauth.account.signals import user_signed_up
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

from logger import setup_logging, logger

# Логирование
setup_logging()


@receiver(user_signed_up, sender=User)
def create_profile(sender: User, **kwargs) -> Profile:
    """Создает профиль после регистрации пользователя.

    Args:
        sender (User): Модель, которая посылает сигнал,
        о создании нового пользователя.

    Returns:
        Profile: Профиль пользователя.
    """
    user = kwargs["user"]
    try:
        profile = Profile.objects.get_or_create(user=user)
        logger.debug(f"Создан профиль {user}")
    except Exception as exc:
        logger.exception(exc)
    return profile
