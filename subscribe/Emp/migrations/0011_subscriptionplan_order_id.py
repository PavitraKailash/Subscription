# Generated by Django 3.2.7 on 2021-09-19 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Emp', '0010_alter_subscriptionplan_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='order_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Emp.order'),
        ),
    ]
