# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-26 07:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('interaction', '0001_initial'),
        ('ligand', '0001_initial'),
        ('residue', '0001_initial'),
        ('common', '0001_initial'),
        ('protein', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fragment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ligand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ligand.Ligand')),
            ],
            options={
                'db_table': 'structure_fragment',
            },
        ),
        migrations.CreateModel(
            name='PdbData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdb', models.TextField()),
            ],
            options={
                'db_table': 'structure_pdb_data',
            },
        ),
        migrations.CreateModel(
            name='Rotamer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdbdata', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.PdbData')),
                ('residue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='residue.Residue')),
            ],
            options={
                'db_table': 'structure_rotamer',
            },
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_chain', models.CharField(max_length=20)),
                ('resolution', models.DecimalField(decimal_places=3, max_digits=5)),
                ('publication_date', models.DateField()),
                ('representative', models.BooleanField(default=False)),
                ('ligands', models.ManyToManyField(through='interaction.StructureLigandInteraction', to='ligand.Ligand')),
                ('pdb_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.WebLink')),
                ('pdb_data', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='structure.PdbData')),
                ('protein_anomalies', models.ManyToManyField(to='protein.ProteinAnomaly')),
                ('protein_conformation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinConformation')),
                ('publication', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Publication')),
            ],
            options={
                'db_table': 'structure',
            },
        ),
        migrations.CreateModel(
            name='StructureCoordinates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'structure_coordinates',
            },
        ),
        migrations.CreateModel(
            name='StructureCoordinatesDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'db_table': 'structure_coordinates_description',
            },
        ),
        migrations.CreateModel(
            name='StructureEngineering',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'structure_engineering',
            },
        ),
        migrations.CreateModel(
            name='StructureEngineeringDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'db_table': 'structure_engineering_description',
            },
        ),
        migrations.CreateModel(
            name='StructureModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdb', models.TextField()),
                ('main_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Structure')),
                ('protein', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.Protein')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinState')),
            ],
            options={
                'db_table': 'structure_model',
            },
        ),
        migrations.CreateModel(
            name='StructureModelAnomalies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=1)),
                ('anomaly', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinAnomaly')),
                ('homology_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.StructureModel')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Structure')),
            ],
            options={
                'db_table': 'structure_model_anomalies',
            },
        ),
        migrations.CreateModel(
            name='StructureModelLoopTemplates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('homology_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.StructureModel')),
                ('segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinSegment')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Structure')),
            ],
            options={
                'db_table': 'structure_model_loop_templates',
            },
        ),
        migrations.CreateModel(
            name='StructureModelResidues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence_number', models.IntegerField()),
                ('origin', models.CharField(max_length=15)),
                ('homology_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.StructureModel')),
                ('residue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='residue.Residue')),
                ('rotamer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='structure.Rotamer')),
                ('segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinSegment')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='structure.Structure')),
            ],
            options={
                'db_table': 'structure_model_residues',
            },
        ),
        migrations.CreateModel(
            name='StructureSegment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.IntegerField()),
                ('end', models.IntegerField()),
                ('protein_segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinSegment')),
                ('structure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Structure')),
            ],
            options={
                'db_table': 'structure_segment',
            },
        ),
        migrations.CreateModel(
            name='StructureSegmentModeling',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.IntegerField()),
                ('end', models.IntegerField()),
                ('protein_segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinSegment')),
                ('structure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Structure')),
            ],
            options={
                'db_table': 'structure_segment_modeling',
            },
        ),
        migrations.CreateModel(
            name='StructureStabilizingAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'structure_stabilizing_agent',
            },
        ),
        migrations.CreateModel(
            name='StructureType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'structure_type',
            },
        ),
        migrations.AddField(
            model_name='structureengineering',
            name='description',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.StructureEngineeringDescription'),
        ),
        migrations.AddField(
            model_name='structureengineering',
            name='protein_segment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinSegment'),
        ),
        migrations.AddField(
            model_name='structureengineering',
            name='structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Structure'),
        ),
        migrations.AddField(
            model_name='structurecoordinates',
            name='description',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.StructureCoordinatesDescription'),
        ),
        migrations.AddField(
            model_name='structurecoordinates',
            name='protein_segment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinSegment'),
        ),
        migrations.AddField(
            model_name='structurecoordinates',
            name='structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Structure'),
        ),
        migrations.AddField(
            model_name='structure',
            name='stabilizing_agents',
            field=models.ManyToManyField(to='structure.StructureStabilizingAgent'),
        ),
        migrations.AddField(
            model_name='structure',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protein.ProteinState'),
        ),
        migrations.AddField(
            model_name='structure',
            name='structure_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.StructureType'),
        ),
        migrations.AddField(
            model_name='rotamer',
            name='structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Structure'),
        ),
        migrations.AddField(
            model_name='fragment',
            name='pdbdata',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.PdbData'),
        ),
        migrations.AddField(
            model_name='fragment',
            name='residue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='residue.Residue'),
        ),
        migrations.AddField(
            model_name='fragment',
            name='structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Structure'),
        ),
    ]