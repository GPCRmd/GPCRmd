# Generated by Django 4.1.5 on 2023-05-03 10:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dynadb', '0117_alter_dyndbfilesdynamics_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllDownloads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tmpname', models.CharField(max_length=80, unique=True)),
                ('creation_timestamp', models.DateTimeField()),
                ('created_by_dbengine', models.CharField(max_length=40)),
                ('last_update_by_dbengine', models.CharField(max_length=40)),
                ('created_by', models.IntegerField(blank=True, null=True)),
                ('last_update_by', models.IntegerField(blank=True, null=True)),
                ('filepath', models.CharField(blank=True, max_length=520, null=True)),
                ('url', models.CharField(blank=True, max_length=520, null=True)),
                ('id_file_types', models.ForeignKey(db_column='id_file_types', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dynadb.dyndbfiletypes')),
            ],
            options={
                'db_table': 'download_files',
                'managed': True,
            },
        ),
    ]
