# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-12-22 16:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0064_auto_20161221_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbcomplexcompound',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Orthosteric ligand'), (1, 'Allosteric ligand')], default=0),
        ),
        migrations.AlterField(
            model_name='dyndbcomplexmoleculemolecule',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Orthosteric ligand'), (1, 'Allosteric ligand')], default=0),
        ),
        migrations.AlterField(
            model_name='dyndbdynamicscomponents',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Ions'), (1, 'Lipid'), (2, 'Water'), (3, 'Other')], default=0),
        ),
        migrations.AlterField(
            model_name='dyndbmodelcomponents',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Ions'), (1, 'Ligand'), (2, 'Lipid'), (3, 'Water'), (4, 'Other')], default=0),
        ),
        migrations.AlterField(
            model_name='dyndbsubmissionmolecule',
            name='type',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Orthosteric ligand'), (1, 'Allosteric ligand'), (2, 'Crystallographic ions'), (3, 'Crystallographic lipids'), (4, 'Crystallographic waters'), (5, 'Other co-crystalized item'), (6, 'Bulky waters'), (7, 'Bulky lipids'), (8, 'Bulky ions'), (9, 'Other bulk component')], default=0, null=True),
        ),
    ]
