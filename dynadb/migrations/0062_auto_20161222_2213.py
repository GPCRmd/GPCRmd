# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-12-22 21:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0061_auto_20161207_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbmodeledresidues',
            name='bonded_to_id_modeled_residues',
            field=models.ForeignKey(blank=True, db_column='bond_to_id_modeled_residues', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='dyndbmodeledresidues_bond_to_id_modeled_residues', to='dynadb.DyndbModeledResidues'),
        ),
        migrations.AlterField(
            model_name='dyndbmodeledresidues',
            name='id_model',
            field=models.ForeignKey(db_column='id_model', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbModel'),
        ),
        migrations.AlterField(
            model_name='dyndbmodeledresidues',
            name='template_id_model',
            field=models.ForeignKey(blank=True, db_column='template_id_model', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='dyndbmodeledresidues_template_id_protein', to='dynadb.DyndbModel'),
        ),
    ]
