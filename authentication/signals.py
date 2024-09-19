from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User
from userpreferences.models import UserPreference


@receiver(post_save, sender=User, dispatch_uid="update_stock_count")
def create_user_preference(sender, instance, **kwargs):
    UserPreference.objects.create(user = instance)    
