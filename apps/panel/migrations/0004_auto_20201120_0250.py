# Generated by Django 3.1.3 on 2020-11-20 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0003_product_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='rating',
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
