# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-15 07:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0092_dyndbefficacy_reference_id_efficacy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbexpinteractiondata',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Functional'), (1, 'Binding'), (2, 'Efficacy'), (3, 'Inhibition')], default=0),
        ),
    ]
