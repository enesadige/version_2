# Generated by Django 5.1.7 on 2025-05-02 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_profile_temporary_email_alter_profile_role_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Kullanıcı Profili', 'verbose_name_plural': 'Kullanıcı Profilleri'},
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('student', 'Öğrenci'), ('community', 'Topluluk')], default='student', max_length=20),
        ),
    ]
