# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-02-01 13:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0078_auto_20170201_1044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dyndbcomplexexp',
            name='ec_fifty',
        ),
        migrations.RemoveField(
            model_name='dyndbcomplexexp',
            name='ic_fifty',
        ),
        migrations.RemoveField(
            model_name='dyndbcomplexexp',
            name='kd',
        ),
        migrations.RemoveField(
            model_name='dyndbcomplexexp',
            name='ki',
        ),
    ]