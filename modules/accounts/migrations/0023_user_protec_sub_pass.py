# Generated by Django 4.1.5 on 2023-06-19 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_user_has_privilege_covid'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='protec_sub_pass',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]
