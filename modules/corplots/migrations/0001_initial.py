# Generated by Django 4.1.5 on 2024-05-02 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Corplots',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dyn_id', models.IntegerField(blank=True, null=True)),
                ('drug', models.CharField(blank=True, max_length=30, null=True)),
                ('name', models.TextField(max_length=100)),
                ('receptor', models.CharField(blank=True, max_length=30, null=True)),
            ],
            options={
                'db_table': 'corplots',
            },
        ),
    ]