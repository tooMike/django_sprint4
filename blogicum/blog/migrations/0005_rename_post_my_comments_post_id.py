# Generated by Django 3.2.16 on 2024-02-23 06:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_rename_post_comments_post_my'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comments',
            old_name='post_my',
            new_name='post_id',
        ),
    ]
