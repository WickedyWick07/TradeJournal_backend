# Generated by Django 5.1.1 on 2024-09-29 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0005_alter_journalentry_target_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalentry',
            name='lot_size',
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
    ]
