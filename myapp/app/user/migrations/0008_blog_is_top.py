# Generated by Django 2.2.5 on 2020-07-10 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20200710_0153'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='is_top',
            field=models.IntegerField(default=0, null=True),
        ),
    ]