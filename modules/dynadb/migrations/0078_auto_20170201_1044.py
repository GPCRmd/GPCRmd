# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-02-01 09:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0077_auto_20170126_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbreferences',
            name='journal_press',
            field=models.CharField(blank=True, help_text='Name of the Journal or Press in case of a book.', max_length=200, null=True, verbose_name='Journal or Press'),
        ),
    ]
