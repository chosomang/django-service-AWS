# Generated by Django 3.0.8 on 2023-09-20 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TeirenSIEM', '0008_auto_20230913_0227'),
    ]

    operations = [
        migrations.AddField(
            model_name='gridlayout',
            name='isDefault',
            field=models.BooleanField(default=False),
        ),
    ]
