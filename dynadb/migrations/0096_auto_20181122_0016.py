# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-11-21 23:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0095_auto_20181017_2010'),
    ]

    operations = [
        migrations.AddField(
            model_name='dyndbsubmissiondynamicsfiles',
            name='id_files',
            field=models.ForeignKey(blank=True, db_column='id_files', default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.DyndbFiles'),
        ),
        migrations.AlterField(
            model_name='dyndbfilesdynamics',
            name='framenum',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]
