# Generated by Django 5.1.1 on 2024-09-29 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0003_accountjournal_user_alter_journalentry_journal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalentry',
            name='entry_price',
            field=models.DecimalField(decimal_places=5, max_digits=10),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='lot_size',
            field=models.DecimalField(decimal_places=5, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='stop_loss_price',
            field=models.DecimalField(decimal_places=5, max_digits=10),
        ),
    ]
