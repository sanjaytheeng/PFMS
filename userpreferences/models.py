from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserPreference(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE,related_name='user_preference')
    currency = models.CharField(max_length=255, blank=True, null=True,default="NPR - Nepali Rupees")
    premium = models.BooleanField(default=False,null=True)
    subscription_until = models.DateField(verbose_name="Subscription Until",null=True,blank=True)

    def __str__(self):
        return str(self.user)+'s' + 'preferences'
    
    @property
    def get_curr(self):
        return self.currency.split(" - ")[0]
