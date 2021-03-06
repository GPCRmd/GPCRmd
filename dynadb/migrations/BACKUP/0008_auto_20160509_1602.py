# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-09 14:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0007_auto_20160506_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbdynamics',
            name='id_assay_types',
            field=models.ForeignKey(blank=True, db_column='id_assay_types', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbAssayTypes'),
        ),
        migrations.AlterField(
            model_name='dyndbdynamics',
            name='id_dynamics_membrane_types',
            field=models.ForeignKey(blank=True, db_column='id_dynamics_membrane_types', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbDynamicsMembraneTypes'),
        ),
        migrations.AlterField(
            model_name='dyndbdynamics',
            name='id_dynamics_methods',
            field=models.ForeignKey(blank=True, db_column='id_dynamics_methods', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbDynamicsMethods'),
        ),
        migrations.AlterField(
            model_name='dyndbdynamics',
            name='id_dynamics_solvent_types',
            field=models.ForeignKey(blank=True, db_column='id_dynamics_solvent_types', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbDynamicsSolventTypes'),
        ),
        migrations.AlterField(
            model_name='dyndbdynamics',
            name='id_model',
            field=models.ForeignKey(blank=True, db_column='id_model', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbModel'),
        ),
        migrations.AlterField(
            model_name='dyndbdynamics',
            name='submission_id',
            field=models.ForeignKey(blank=True, db_column='submission_id', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbSubmission'),
        ),
        migrations.AlterField(
            model_name='dyndbsubmissionprotein',
            name='submission_id',
            field=models.ForeignKey(blank=True, db_column='submission_id', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbSubmission'),
        ),
    ]
