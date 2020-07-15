from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# box model
class Box(models.Model):
    length = models.FloatField(null=True, blank=False)
    width = models.FloatField(null=True, blank=False)
    height = models.FloatField(null=True, blank=False)
    area = models.FloatField(null=True, blank=False)
    volume = models.FloatField(null=True, blank=False)
    created_by = models.ForeignKey(User, null=True, blank=False, editable=False, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)
    # updated date will be added automatically because of auto_now attribute
    last_updated = models.DateTimeField(auto_now=True)


class Store(models.Model):
    employee = models.ManyToManyField(User)
    box = models.ManyToManyField(Box)

# signal to create token for authentication once the user is created
@receiver(post_save, sender=User)
def create_token(sender, instance,**kwargs):
    token, created = Token.objects.get_or_create(user=instance)

post_save.connect(create_token, sender=User)