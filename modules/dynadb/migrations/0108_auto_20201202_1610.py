# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2020-12-02 15:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0107_auto_20201202_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbfilesnongpcr',
            name='filepath',
            field=models.CharField(blank=True, max_length=520, null=True, unique=True),
        ),
    ]