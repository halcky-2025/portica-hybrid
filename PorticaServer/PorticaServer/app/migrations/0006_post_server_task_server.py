# Generated by Django 4.1.2 on 2022-10-26 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_task_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="post", name="server", field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="task", name="server", field=models.TextField(default=""),
        ),
    ]
