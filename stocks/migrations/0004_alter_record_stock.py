# Generated by Django 4.2 on 2023-06-13 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0003_alter_record_stock_alter_stcokinhand_buyamount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='stock',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_code', to='stocks.stcokinhand'),
        ),
    ]