# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-28 10:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0010_auto_20160623_1636'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dyndbdynamicscomponents',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbmodel',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dyndbmodelcomponents',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='dyndbreferences',
            options={'managed': True},
        ),
        migrations.DeleteModel(
            name='DyndbMembraneComponents',
        ),
        migrations.DeleteModel(
            name='DyndbIonicComponents',
        ),
        migrations.AlterField(
            model_name='DyndbModel',
            name='source_type',
            field=models.SmallIntegerField(choices=((0,'X-ray'),(1,'NMR'),(2,'Docking'),(3,'MD'),(4,'Other')), default=0),
        ),
    ]