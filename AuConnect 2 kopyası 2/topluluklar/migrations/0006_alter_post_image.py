# Generated by Django 5.1.7 on 2025-05-07 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topluluklar', '0005_alter_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='static/media/post_images/', verbose_name='Resim'),
        ),
    ]
