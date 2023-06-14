# Generated by Django 4.2 on 2023-06-13 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StcokInHand',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=6)),
                ('name', models.CharField(max_length=20)),
                ('close', models.DecimalField(decimal_places=3, max_digits=8)),
                ('ratio', models.DecimalField(decimal_places=3, max_digits=8)),
                ('preclose', models.DecimalField(decimal_places=3, max_digits=8)),
                ('buyquantity', models.IntegerField()),
                ('buyamount', models.DecimalField(decimal_places=3, max_digits=11)),
                ('sellquantity', models.IntegerField()),
                ('sellamount', models.DecimalField(decimal_places=3, max_digits=11)),
                ('quantityinhand', models.IntegerField()),
                ('profit', models.DecimalField(decimal_places=3, max_digits=11)),
                ('estimation', models.DecimalField(decimal_places=3, default=0, max_digits=11)),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('mark', models.CharField(max_length=4)),
                ('quantity', models.IntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=3, default=0, max_digits=8)),
                ('amount', models.DecimalField(decimal_places=3, default=0, max_digits=11)),
                ('date', models.DateField(auto_now_add=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stcokinhand')),
            ],
        ),
    ]
