# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-19 10:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20160719_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.CharField(default='def', max_length=200),
            preserve_default=False,
        ),
    ]