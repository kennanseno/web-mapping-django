# from django.db import models
from django.utils import timezone
from django.contrib.gis.geos import Point

from django.contrib.gis.db import models
from django.contrib.gis import geos
from django.contrib.auth.models import AbstractUser

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    last_location = models.PointField(
        verbose_name="last known location",
        blank=True,
        null=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    modified = models.DateTimeField(
        auto_now=True
    )

    # objects = models.GeoManager()

    def __str__(self):
        return "{}, ({}), last seen at {} ... cr={}, mod={}" \
            .format(self.username, self.get_full_name(), self.last_location, self.created, self.modified)


class BusStop(models.Model):
    class Meta:
        verbose_name = "bus stop"
        verbose_name_plural = "bus stops"

    address = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="address"
    )
    location = models.PointField(
        verbose_name="location",
        blank=True,
        null=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    modified = models.DateTimeField(
        auto_now=True
    )

    # objects = models.Manager()

    def __str__(self):
        return "{} with location of ({})".format(self.address, self.location)


class Favourite(models.Model):
    class Meta:
        unique_together = ['user', 'stop']
        verbose_name = "favourite bus stop"
        verbose_name_plural = "favourite bus stops"

    user = models.ForeignKey(
        User,
        verbose_name="user",
        on_delete=models.CASCADE
    )
    stop = models.ForeignKey(
        BusStop,
        verbose_name="bus stop",
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    modified = models.DateTimeField(
        auto_now=True
    )

    # objects = models.Manager()

    def __str__(self):
        return "Bus stop {} is a favourite of {}".format(self.stop, self.user)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
