# Generated by Django 4.1.9 on 2024-01-15 05:06

import compliance.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compliance', '0002_asset_evidence_policy_alter_document_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evidence',
            name='uploadedFile',
            field=models.FileField(upload_to=compliance.models.evidence_directory_path),
        ),
    ]