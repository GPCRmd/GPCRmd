# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-11 16:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0044_auto_20161005_1136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dyndbcomplexprotein',
            name='is_receptor',
        ),
    ]