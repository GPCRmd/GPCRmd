# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2020-12-04 11:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0110_auto_20201203_1217'),
    ]

    operations = [
        migrations.CreateModel(
            name='DyndbReferencesNonGPCRDynamics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_ngpcr_dynamics', models.ForeignKey(db_column='id_ngpcr_dynamics', on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbNonGPCRDynamics')),
                ('id_references', models.ForeignKey(db_column='id_references', on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbReferences')),
            ],
            options={
                'managed': True,
                'db_table': 'dyndb_references_nongpcrdynamics',
            },
        ),
        migrations.AddField(
            model_name='dyndbfilesnongpcr',
            name='author_institution',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='dyndbfilesnongpcr',
            name='author_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='dyndbreferencesnongpcrdynamics',
            unique_together=set([('id_ngpcr_dynamics', 'id_references')]),
        ),
    ]