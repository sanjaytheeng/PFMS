# Generated by Django 5.0.7 on 2024-08-10 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterField(
            model_name='expense',
            name='description',
            field=models.TextField(max_length=200),
        ),
    ]
