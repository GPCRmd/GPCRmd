# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2020-09-22 13:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_remove_user_act_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_privilege_covid',
            field=models.BooleanField(default=False),
        ),
    ]