# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2020-12-14 14:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('covid19', '0024_auto_20201211_1251'),
    ]

    operations = [
        migrations.CreateModel(
            name='CovidIsolate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isolate_name', models.CharField(blank=True, max_length=200, null=True)),
                ('ymd', models.DateField(blank=True, null=True)),
                ('isolate_id', models.CharField(blank=True, max_length=100, null=True)),
                ('history', models.CharField(blank=True, max_length=200, null=True)),
                ('tloc', models.CharField(blank=True, max_length=200, null=True)),
                ('host', models.CharField(blank=True, max_length=200, null=True)),
                ('originating_lab', models.CharField(blank=True, max_length=500, null=True)),
                ('submitting_lab', models.CharField(blank=True, max_length=500, null=True)),
                ('submitter', models.CharField(blank=True, max_length=500, null=True)),
                ('location', models.CharField(blank=True, max_length=200, null=True)),
                ('isolate_type', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CovidMutations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resid', models.SmallIntegerField(null=True)),
                ('resletter_from', models.CharField(max_length=1, null=True)),
                ('resletter_to', models.CharField(max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CovidSequence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_wt', models.BooleanField(default=True)),
                ('seq', models.CharField(blank=True, max_length=3000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CovidSequencedGene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alt_name', models.CharField(blank=True, max_length=50, null=True)),
                ('id_final_protein', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='covid19.CovidFinalProtein')),
                ('id_isolate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='covid19.CovidIsolate')),
                ('id_sequence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='covid19.CovidSequence')),
            ],
        ),
        migrations.AddField(
            model_name='covidmutations',
            name='id_sequence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='covid19.CovidSequence'),
        ),
    ]