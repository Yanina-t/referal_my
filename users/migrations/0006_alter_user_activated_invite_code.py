# Generated by Django 5.0.3 on 2024-04-14 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_activated_invite_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='activated_invite_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Чужой инвайт-код'),
        ),
    ]
