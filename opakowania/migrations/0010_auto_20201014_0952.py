# Generated by Django 3.1 on 2020-10-14 09:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opakowania', '0009_auto_20201010_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='customer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='opakowania.customer'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='offer',
            name='status',
            field=models.IntegerField(choices=[(1, 'Nowa')], default=1),
        ),
    ]
