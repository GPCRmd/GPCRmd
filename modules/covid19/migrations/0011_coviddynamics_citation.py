# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2020-10-21 14:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covid19', '0010_coviddynamicscomponents_is_membrane'),
    ]

    operations = [
        migrations.AddField(
            model_name='coviddynamics',
            name='citation',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
