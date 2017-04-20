# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-19 16:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20170419_1607'),
    ]

    operations = [
        migrations.RenameField(
            model_name='favourite',
            old_name='favourite',
            new_name='user',
        ),
        migrations.RemoveField(
            model_name='busstop',
            name='favourites',
        ),
        migrations.AlterUniqueTogether(
            name='favourite',
            unique_together=set([('user', 'stop')]),
        ),
    ]
