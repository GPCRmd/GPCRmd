# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-02-16 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0084_auto_20170216_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='dyndbcomplexexp',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
    ]
