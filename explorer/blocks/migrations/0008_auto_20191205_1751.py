# Generated by Django 3.0 on 2019-12-05 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blocks', '0007_auto_20191205_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='txinput',
            name='witness',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
