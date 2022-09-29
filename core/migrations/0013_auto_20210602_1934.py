# Generated by Django 3.2 on 2021-06-02 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_transaction_made_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='made_by',
        ),
        migrations.AddField(
            model_name='transaction',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
    ]