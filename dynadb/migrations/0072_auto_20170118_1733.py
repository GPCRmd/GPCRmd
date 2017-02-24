# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-18 16:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0071_auto_20170117_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbreferences',
            name='url',
            field=models.CharField(blank=True, help_text='Uniform Resource Locator to the publication resource', max_length=800, null=True, verbose_name='URL'),
        ),
    ]