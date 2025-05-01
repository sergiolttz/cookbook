import os
from uuid import uuid4
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.files.base import ContentFile
from PIL import Image
from django.contrib.auth.models import User
from .models import Recipe, UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

@receiver(pre_save, sender=Recipe)
def rename_recipe_image(sender, instance, **kwargs):
    image_field = instance.image
    if not image_field or not hasattr(image_field, 'file'):
        return

    # Si es edición y la imagen no cambió, no hacemos nada
    if instance.pk:
        try:
            old_instance = Recipe.objects.get(pk=instance.pk)
            if old_instance.image == instance.image:
                return
        except Recipe.DoesNotExist:
            pass

    ext = os.path.splitext(image_field.name)[1]
    new_filename = f"{slugify(instance.title)}-{uuid4().hex[:8]}{ext}"

    image_field.file.seek(0)
    img = Image.open(image_field.file)
    img_format = img.format if img.format else 'JPEG'

    max_size = (1200, 1200)
    if img.height > 1200 or img.width > 1200:
        img.thumbnail(max_size)

    img_file = ContentFile(b"")
    img.save(img_file, format=img_format)
    img_file.seek(0)

    instance.image.save(new_filename, img_file, save=False)

@receiver(pre_save, sender=UserProfile)
def rename_profile_picture(sender, instance, **kwargs):
    image_field = instance.profile_picture
    if not image_field or not hasattr(image_field, 'file'):
        return

    # Si no cambió la imagen, salimos
    if instance.pk:
        try:
            old_instance = UserProfile.objects.get(pk=instance.pk)
            if old_instance.profile_picture == instance.profile_picture:
                return
        except UserProfile.DoesNotExist:
            pass

    ext = os.path.splitext(image_field.name)[1]
    new_filename = f"{slugify(instance.user.username)}-profile-{uuid4().hex[:8]}{ext}"

    image_field.file.seek(0)
    img = Image.open(image_field.file)
    img_format = img.format if img.format else 'JPEG'

    max_size = (600, 600)
    if img.height > 600 or img.width > 600:
        img.thumbnail(max_size)

    img_file = ContentFile(b"")
    img.save(img_file, format=img_format)
    img_file.seek(0)

    instance.profile_picture.save(new_filename, img_file, save=False)