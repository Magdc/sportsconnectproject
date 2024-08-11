from django.db import models

# Create your models here.

class User(models.Model):
    idUser = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    lastname1 = models.CharField(max_length=20)
    lastname2 = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    phone = models.IntegerField()


class Facilities(models.Model):
    idFacility = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='reservation/facilities/')

class Availability(models.Model):
    facilities = models.ForeignKey(Facilities, null=True, on_delete=models.CASCADE)
    day = models.IntegerField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday')
        ]
    )
    start = models.TimeField()
    end = models.TimeField()
    available = models.BooleanField(default=True)

class Reservation(models.Model):
    facilities = models.ForeignKey(Facilities, on_delete=models.CASCADE)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    date = models.DateField()
    start = models.TimeField
    end = models.TimeField()

