# Generated by Django 4.2 on 2023-06-14 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0005_profit_stcokinhand_profit_day_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stcokinhand',
            name='profit_ratio',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]