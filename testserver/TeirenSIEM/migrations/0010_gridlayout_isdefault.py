# Generated by Django 4.1.9 on 2023-09-19 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TeirenSIEM', '0009_alter_gridlayout_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='gridlayout',
            name='isDefault',
            field=models.BooleanField(default=False),
        ),
    ]
