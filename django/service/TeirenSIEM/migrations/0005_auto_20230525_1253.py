# Generated by Django 3.0.8 on 2023-05-25 03:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TeirenSIEM', '0004_auto_20230522_1440'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ncplogs',
            options={'managed': False},
        ),
        migrations.AlterModelTable(
            name='admins',
            table='weather',
        ),
        migrations.AlterModelTable(
            name='ncplogs',
            table='startup_log',
        ),
    ]
