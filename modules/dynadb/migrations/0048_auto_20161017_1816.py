# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-17 16:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0047_auto_20161017_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='dyndbcomplexmolecule',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Orthosteric ligand'), (1, 'Allosteric ligand'), (2, 'Crystallographic waters'), (3, 'Other')], default=0),
        ),
    ]
