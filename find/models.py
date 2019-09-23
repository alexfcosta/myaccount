from django.db import models


class Customers(models.Model):
    gid = models.CharField(max_length=50)
    title = models.CharField(max_length=5)
    initial = models.CharField(max_length=1)
    forename = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    status = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    contact_type = models.CharField(max_length=20)
    contact_value = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=50)
    address_line2 = models.CharField(max_length=50)



