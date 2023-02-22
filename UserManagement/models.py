from django.db import models
from django.core.exceptions import ValidationError

def digitsOnly(value):
    if value.isdigit() == False or value.size() != 4:
        raise ValidationError('Employee number must contain 4 digits')

# Create your models here.
class User(models.Model):
    name = models.CharField(
        max_length=20,
        blank=False,
        null=False
    )
    number = models.CharField(
        primary_key=True,
        max_length=4,
        blank = False,
        validators=[digitsOnly],
        null=False
    )
    role = models.CharField(
        max_length=8,
        blank = False,
        null=False,
    )
    password = models.CharField(
        max_length=100,
        blank = False,
        null=False
    )