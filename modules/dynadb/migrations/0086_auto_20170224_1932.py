# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-24 18:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0085_auto_20170217_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbmodel',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Apoform (one single protein monomer)'), (1, 'Complex')], default=0),
        ),
    ]