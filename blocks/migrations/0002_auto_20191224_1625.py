# Generated by Django 3.0.1 on 2019-12-24 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blocks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockrow',
            name='bits',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='blockrow',
            name='hash_id',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='blockrow',
            name='merkle_root',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='blockrow',
            name='nonce',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='blockrow',
            name='prev_block',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='hash_id',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='txinput',
            name='prev_tx',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='txinput',
            name='script_sig',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='txinput',
            name='witness',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='txoutput',
            name='address',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='txoutput',
            name='op_return_data',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='txoutput',
            name='output_type',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='txoutput',
            name='script_pubkey',
            field=models.CharField(max_length=200),
        ),
    ]
