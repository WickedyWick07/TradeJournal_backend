# Generated by Django 5.1.1 on 2024-09-23 13:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_price', models.DecimalField(decimal_places=3, max_digits=10)),
                ('stop_loss_price', models.DecimalField(decimal_places=3, max_digits=10)),
                ('target_price', models.DecimalField(decimal_places=3, max_digits=10)),
                ('result', models.CharField(choices=[('win', 'WIN'), ('loss', 'LOSS'), ('break-even', 'BREAK-EVEN')], max_length=50)),
                ('pair', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('image', models.ImageField(upload_to='journal_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
