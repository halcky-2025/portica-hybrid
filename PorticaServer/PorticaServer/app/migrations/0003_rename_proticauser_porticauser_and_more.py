# Generated by Django 4.1.1 on 2022-10-07 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_task_key"),
    ]

    operations = [
        migrations.RenameModel(old_name="ProticaUser", new_name="PorticaUser",),
        migrations.RenameField(
            model_name="twitteruser", old_name="tweeter_id", new_name="twitter_id",
        ),
        migrations.AddField(
            model_name="post", name="totask", field=models.TextField(default=""),
        ),
    ]
