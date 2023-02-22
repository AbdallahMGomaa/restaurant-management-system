# Generated by Django 4.1.7 on 2023-02-22 10:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TableManagement', '0006_remove_table_reserved'),
        ('ReservationManagement', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TableManagement.table'),
        ),
    ]