# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-12-21 17:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0063_auto_20161221_1826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbsubmissionmolecule',
            name='type',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Orthosteric ligand'), (1, 'Allosteric ligand'), (2, 'Crystallographic waters'), (3, 'Crystallographic lipids'), (4, 'Crystallographic ions'), (5, 'Other co-crystalized item'), (6, 'Bulky waters'), (7, 'Bulky lipids'), (8, 'Bulky ions'), (9, 'Other bulk component')], default=0, null=True),
        ),
    ]
