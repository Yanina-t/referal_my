# Generated by Django 5.0.3 on 2024-04-11 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_is_authenticated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=12, unique=True, verbose_name='Номер телефона'),
        ),
    ]
