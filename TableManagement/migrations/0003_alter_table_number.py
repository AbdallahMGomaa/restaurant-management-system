# Generated by Django 4.1.7 on 2023-02-21 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TableManagement', '0002_remove_table_id_table_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='number',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
