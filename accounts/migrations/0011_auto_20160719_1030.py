# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-19 10:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20160715_0914'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(default='def country', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='lab',
            field=models.CharField(default='def lab', max_length=200),
            preserve_default=False,
        ),
    ]
