# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-11-25 00:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0096_auto_20181122_0016'),
    ]

    operations = [
        migrations.AddField(
            model_name='dyndbsubmissiondynamicsfiles',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='dyndbsubmissiondynamicsfiles',
            name='to_delete',
            field=models.BooleanField(default=False),
        ),
    ]
