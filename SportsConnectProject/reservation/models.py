from django.db import models
from django.conf import settings
from datetime import time
from django.utils import timezone
from django.contrib.auth.models import User
from facility.models import Facilities, Availability

# Create your models here.

class Reservation(models.Model):
    idUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    facilities = models.ForeignKey(Facilities, on_delete=models.CASCADE)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return (f"Usuario #{self.idUser} - {self.facilities.name}. [{self.availability.date} - {self.availability.time_slot}]")
    
class WaitList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    facilities = models.ForeignKey(Facilities, on_delete=models.CASCADE)
    date = models.DateField() 
    date_added = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} espera para {self.facilities.name} el {self.date}"

