# Generated by Django 4.1.5 on 2023-06-19 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_user_protec_sub_pass'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='protec_sub_pass',
            field=models.BinaryField(),
        ),
    ]