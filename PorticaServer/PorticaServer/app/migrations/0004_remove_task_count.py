# Generated by Django 4.1.1 on 2022-10-23 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_rename_proticauser_porticauser_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="task", name="count",),
    ]
