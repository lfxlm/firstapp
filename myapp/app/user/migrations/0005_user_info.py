# Generated by Django 2.2.5 on 2020-07-10 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20200710_0038'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='info',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
