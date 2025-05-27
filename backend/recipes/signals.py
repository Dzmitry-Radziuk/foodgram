import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from recipes.models import Recipe


@receiver(post_delete, sender=Recipe)
def delete_image_on_recipe_delete(sender, instance, **kwargs):
    """
    Обработчик сигнала post_delete для модели Recipe.

    При удалении объекта Recipe проверяет, есть ли связанный файл изображения,
    и удаляет его с файловой системы, чтобы не оставлять мусор.

    Args:
        sender: Класс модели, которая вызвала сигнал (Recipe).
        instance: Удаляемый экземпляр модели Recipe.
        **kwargs: Дополнительные параметры.
    """
    if instance.image and instance.image.path:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(pre_save, sender=Recipe)
def delete_old_image_on_change(sender, instance, **kwargs):
    """
    Обработчик сигнала pre_save для модели Recipe.

    Перед сохранением объекта проверяет, изменилось ли поле изображения.
    Если да, то удаляет старый файл изображения с диска.

    Args:
        sender: Класс модели, которая вызвала сигнал (Recipe).
        instance: Сохраняемый экземпляр модели Recipe.
        **kwargs: Дополнительные параметры.
    """
    if not instance.pk:
        return

    try:
        old_image = Recipe.objects.get(pk=instance.pk).image
    except Recipe.DoesNotExist:
        return

    new_image = instance.image
    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)
