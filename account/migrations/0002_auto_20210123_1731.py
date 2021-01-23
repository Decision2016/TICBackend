# Generated by Django 3.1.5 on 2021-01-23 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cache',
            fields=[
                ('mark_info', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('public', models.TextField()),
                ('secret', models.TextField()),
                ('timestamp', models.BigIntegerField()),
                ('ip_address', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'tic_cache',
            },
        ),
        migrations.CreateModel(
            name='WebsiteInfo',
            fields=[
                ('_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256)),
                ('record', models.CharField(max_length=256)),
                ('record_switch', models.BooleanField(default=False)),
            ],
        ),
        migrations.DeleteModel(
            name='VXPage',
        ),
        migrations.AddField(
            model_name='adminuser',
            name='google_secret',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='username',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]
