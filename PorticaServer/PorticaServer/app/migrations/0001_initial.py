# Generated by Django 4.1.1 on 2022-09-22 03:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GmailUser",
            fields=[
                ("gu_id", models.AutoField(primary_key=True, serialize=False)),
                ("pu_id", models.IntegerField(default=-1)),
                ("mail", models.TextField(default="")),
                ("icon", models.TextField(default="")),
            ],
        ),
        migrations.CreateModel(
            name="NetUser",
            fields=[
                ("nu_id", models.AutoField(primary_key=True, serialize=False)),
                ("pu_id", models.IntegerField(default=-1)),
                ("registered", models.TextField(default=django.utils.timezone.now)),
                ("gpu", models.TextField(default="")),
                ("gpu_memory", models.FloatField(default=10.0)),
                ("memory", models.FloatField(default=32.0)),
            ],
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("post_id", models.AutoField(primary_key=True, serialize=False)),
                ("secret", models.TextField(default="")),
                ("post_type", models.TextField(default="")),
                ("ip", models.TextField(default="")),
                ("browser", models.TextField(default="")),
                ("prompt", models.TextField(default="")),
                ("output", models.TextField(default="")),
                ("output_type", models.TextField(default="")),
                ("options", models.TextField(default="{}")),
                ("count", models.IntegerField(default=1)),
                ("priority", models.IntegerField(default=1000)),
                ("mute", models.TextField(default="")),
                ("select", models.TextField(default="")),
                ("created", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="ProticaUser",
            fields=[
                ("pu_id", models.AutoField(primary_key=True, serialize=False)),
                ("user_ids", models.TextField(default="")),
                ("registered", models.DateTimeField(default=django.utils.timezone.now)),
                ("name", models.TextField(default="")),
                ("icon", models.TextField(default="")),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("task_id", models.AutoField(primary_key=True, serialize=False)),
                ("post_id", models.IntegerField(default=-1)),
                ("secret", models.TextField(default="")),
                ("post_type", models.TextField(default="")),
                ("ip", models.TextField(default="")),
                ("browser", models.TextField(default="")),
                ("prompt", models.TextField(default="")),
                ("output", models.TextField(default="")),
                ("output_type", models.TextField(default="")),
                ("options", models.TextField(default="{}")),
                ("count", models.IntegerField(default=1)),
                ("priority", models.IntegerField(default=1000)),
                ("created", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="TwitterUser",
            fields=[
                ("tu_id", models.AutoField(primary_key=True, serialize=False)),
                ("pu_id", models.IntegerField(default=-1)),
                ("tweeter_id", models.TextField(default="")),
                ("screen_name", models.TextField(default="")),
                ("icon", models.TextField(default="")),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("user_id", models.AutoField(primary_key=True, serialize=False)),
                ("ips", models.TextField(default="")),
                ("browser", models.TextField(default="")),
                ("group", models.TextField(default="")),
                ("registered", models.DateTimeField(default=django.utils.timezone.now)),
                ("mute", models.TextField(default="")),
            ],
        ),
    ]