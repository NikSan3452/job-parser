from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender: User, **kwargs) -> Profile:
    """Создает профиль после регистрации пользователя.

    Args:
        sender (User): Модель, которая посылает сигнал,
        о создании нового пользователя.

    Returns:
        Profile: Профиль пользователя.
    """
    user = kwargs["instance"]
    return Profile.objects.get_or_create(user=user)
