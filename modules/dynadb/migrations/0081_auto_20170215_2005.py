# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-02-15 19:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0080_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dyndbfilesmodel',
            options={'managed': True},
        ),
    ]