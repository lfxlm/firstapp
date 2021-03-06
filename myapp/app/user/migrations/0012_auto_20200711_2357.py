# Generated by Django 2.2.5 on 2020-07-11 23:57

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_auto_20200711_1327'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(default='', verbose_name='文章内容')),
            ],
            options={
                'verbose_name': '博客内容表',
                'verbose_name_plural': '博客内容表',
                'db_table': 't_content',
            },
        ),
        migrations.AddField(
            model_name='blog',
            name='read_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='blog',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_content', to='user.BlogContent'),
        ),
    ]
