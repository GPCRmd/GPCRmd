# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-19 14:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0020_auto_20160715_1211'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dyndbprotein',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbsubmissionmodel',
            options={'managed': False},
        ),
    ]