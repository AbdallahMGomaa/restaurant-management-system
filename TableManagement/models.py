from django.db import models

# Create your models here.
class Table(models.Model):
    number = models.IntegerField(primary_key=True)
    seats = models.IntegerField()

