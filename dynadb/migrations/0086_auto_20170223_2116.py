# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-02-23 20:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0085_dyndbcomplexexp_is_published'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dyndbreferencescompound',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbreferencesdynamics',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbreferencesexpinteractiondata',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbreferencesexpproteindata',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbreferencesmodel',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbreferencesmolecule',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbreferencesprotein',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbrelateddynamics',
            options={'managed': True},
        ),
    ]
