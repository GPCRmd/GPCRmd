# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-26 07:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0002_dyndbdynamicscomponents_dyndbmodelcomponents'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dyndbmodeledresidues',
            options={'managed': True},
        ),
    ]
