from allauth.account.signals import user_signed_up

from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


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
    return Profile.objects.create(user=user)
