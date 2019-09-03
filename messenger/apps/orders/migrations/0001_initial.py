# Generated by Django 2.2.3 on 2019-09-03 15:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracking_number', models.CharField(max_length=100)),
                ('cost_of_cards', models.DecimalField(decimal_places=2, max_digits=20)),
                ('transport_fee', models.DecimalField(decimal_places=2, max_digits=20)),
                ('is_cancelled', models.BooleanField(default=False)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=20)),
                ('receiver_fname', models.CharField(default='', max_length=100)),
                ('receiver_lname', models.CharField(default='', max_length=100)),
                ('total_no_of_card_batches', models.IntegerField(default=0)),
                ('mobile_no', models.IntegerField(default=0)),
                ('no_of_regular_batches', models.IntegerField(default=0)),
                ('no_of_premium_batches', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('address', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='address.HomeAddress')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
    ]
