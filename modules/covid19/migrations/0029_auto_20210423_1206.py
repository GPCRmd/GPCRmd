# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2021-04-23 10:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('covid19', '0028_coviddynamics_is_shared_sc2md'),
    ]

    operations = [
        migrations.CreateModel(
            name='CovidMutfincData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uniprot', models.CharField(blank=True, max_length=10, null=True)),
                ('name', models.CharField(blank=True, max_length=10, null=True)),
                ('position', models.SmallIntegerField(blank=True, null=True)),
                ('wt', models.CharField(blank=True, max_length=1, null=True)),
                ('mut', models.CharField(blank=True, max_length=1, null=True)),
                ('freq', models.FloatField(blank=True, null=True)),
                ('ptmmodels', models.CharField(blank=True, max_length=100, null=True)),
                ('sift_score', models.FloatField(blank=True, null=True)),
                ('sift_median', models.FloatField(blank=True, null=True)),
                ('template', models.CharField(blank=True, max_length=8, null=True)),
                ('relative_surface_accessibility', models.FloatField(blank=True, null=True)),
                ('foldx_ddg', models.FloatField(blank=True, null=True)),
                ('mut_escape_mean', models.FloatField(blank=True, null=True)),
                ('mut_escape_max', models.FloatField(blank=True, null=True)),
                ('annotation', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CovidMutfincDataInterface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('int_uniprot', models.CharField(blank=True, max_length=10, null=True)),
                ('interaction_energy', models.FloatField(blank=True, null=True)),
                ('diff_interface_residues', models.FloatField(blank=True, null=True)),
                ('int_name', models.CharField(blank=True, max_length=10, null=True)),
                ('int_template', models.CharField(blank=True, max_length=8, null=True)),
                ('diff_interaction_energy', models.FloatField(blank=True, null=True)),
                ('id_mutfunc_data', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='covid19.CovidMutfincData')),
            ],
        ),
        migrations.AddField(
            model_name='covidmutations',
            name='mutfinc_data',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='covid19.CovidMutfincData'),
        ),
    ]