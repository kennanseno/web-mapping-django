# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-19 15:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20170419_1526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='busstop',
            name='favourites',
        ),
    ]
