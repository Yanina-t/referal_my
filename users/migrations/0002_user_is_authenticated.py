# Generated by Django 5.0.3 on 2024-04-11 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_authenticated',
            field=models.BooleanField(default=False, verbose_name='Авторизован'),
        ),
    ]
