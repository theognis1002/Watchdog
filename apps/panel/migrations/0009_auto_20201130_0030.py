# Generated by Django 3.1.3 on 2020-11-30 00:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('panel', '0008_auto_20201130_0027'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='WatchdogSettings',
            new_name='WatchdogMetaDetails',
        ),
    ]