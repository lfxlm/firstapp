# Generated by Django 2.2.5 on 2020-07-12 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_userlike_is_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='userfollow',
            name='is_follow',
            field=models.IntegerField(default=0, null=True),
        ),
    ]