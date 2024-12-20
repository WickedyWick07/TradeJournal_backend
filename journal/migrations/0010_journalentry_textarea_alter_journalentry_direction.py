# Generated by Django 5.1.1 on 2024-12-11 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0009_alter_journalentry_direction'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalentry',
            name='textarea',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='direction',
            field=models.CharField(choices=[('long', 'LONG'), ('short', 'SHORT')], max_length=5, null=True),
        ),
    ]
