# Generated by Django 3.0.7 on 2020-10-10 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opakowania', '0007_auto_20201010_0711'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='name',
            new_name='customer_name',
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(blank=True, max_length=64, verbose_name='Telefon'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='description',
            field=models.TextField(blank=True, verbose_name='Opis'),
        ),
    ]
