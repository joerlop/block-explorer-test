# Generated by Django 3.0 on 2019-12-16 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blocks', '0010_auto_20191205_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockrow',
            name='hash_id',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]