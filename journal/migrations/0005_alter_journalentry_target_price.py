# Generated by Django 5.1.1 on 2024-09-29 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0004_alter_journalentry_entry_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalentry',
            name='target_price',
            field=models.DecimalField(decimal_places=5, max_digits=10),
        ),
    ]
