# Generated by Django 5.1.7 on 2025-04-23 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topluluklar', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='topluluklar',
            old_name='img',
            new_name='image',
        ),
    ]
