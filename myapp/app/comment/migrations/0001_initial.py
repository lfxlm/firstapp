# Generated by Django 2.2.5 on 2020-07-13 05:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(default=None, max_length=1000, null=True)),
                ('ctime', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subs', to='comment.Comment')),
            ],
            options={
                'db_table': 't_comment',
            },
        ),
        migrations.CreateModel(
            name='CommentImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.CharField(max_length=200)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='com', to='comment.Comment')),
            ],
            options={
                'db_table': 't_comment_image',
            },
        ),
    ]