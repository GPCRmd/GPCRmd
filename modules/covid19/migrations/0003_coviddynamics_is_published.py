# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2020-08-18 08:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covid19', '0002_auto_20200813_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='coviddynamics',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
    ]