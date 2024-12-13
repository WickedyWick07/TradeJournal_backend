# Generated by Django 5.1.1 on 2024-12-13 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0015_remove_journalimage_image_journalimage_image_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journalimage',
            name='image_url',
        ),
        migrations.AddField(
            model_name='journalimage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='journal_images/'),
        ),
    ]
