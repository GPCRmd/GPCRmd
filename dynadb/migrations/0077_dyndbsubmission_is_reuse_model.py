# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-01-26 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0076_auto_20170126_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='dyndbsubmission',
            name='is_reuse_model',
            field=models.BooleanField(default=False),
        ),
    ]
