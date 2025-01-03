# Generated by Django 5.0.7 on 2024-09-17 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpreferences', '0002_alter_userpreference_currency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpreference',
            name='premium',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='userpreference',
            name='subscription_until',
            field=models.DateField(null=True, verbose_name='Subscription Until'),
        ),
    ]
