from django.db import models
from TableManagement.models import Table
# Create your models here.
class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE)