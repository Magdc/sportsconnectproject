from django.db import models
from datetime import time
from django.utils import timezone

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
    date = models.DateField(default=timezone.now)
    time_slot = models.TimeField() 

    # para una facility, en una date determinada, cada time_slot solo se puede asignar una vez
    class Meta:
        unique_together = ('facilities', 'date', 'time_slot')

    def generate_time_slots(self):
        # Generate time slots from 5am to 5pm
        slots = []
        for hour in range(6, 21):
            slots.append(time(hour=hour, minute=0))
        return slots

class Reservation(models.Model):
    facilities = models.ForeignKey(Facilities, on_delete=models.CASCADE)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)

