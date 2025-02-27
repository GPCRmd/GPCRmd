# Generated by Django 4.1.5 on 2025-02-26 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynadb', '0118_dyndbprotein_prot_type_alter_dyndbmodel_source_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dyndbmodel',
            name='source_type',
            field=models.SmallIntegerField(choices=[(0, 'X-ray'), (1, 'NMR'), (2, 'Docking'), (3, 'MD'), (4, 'Electron microscopy (CryoEM)'), (5, 'Other'), (6, 'AlphaFold')], default=0),
        ),
        migrations.AlterField(
            model_name='dyndbmodeledresidues',
            name='source_type',
            field=models.SmallIntegerField(choices=[(0, 'X-ray'), (1, 'NMR'), (2, 'Ab-initio'), (3, 'Homology'), (4, 'Threading'), (5, 'MD'), (6, 'Other Computational Methods'), (7, 'Electron microscopy'), (8, 'AlphaFold')], default=0),
        ),
    ]
