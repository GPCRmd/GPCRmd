# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-12-30 14:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0066_auto_20161223_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbsubmissionmolecule',
            name='type',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Orthosteric ligand'), (1, 'Allosteric ligand'), (2, 'Crystallographic ions'), (3, 'Crystallographic lipids'), (4, 'Crystallographic waters'), (5, 'Other co-crystalized item'), (6, 'Bulk waters'), (7, 'Bulk lipids'), (8, 'Bulk ions'), (9, 'Other bulk component')], default=0, null=True),
        ),
    ]
