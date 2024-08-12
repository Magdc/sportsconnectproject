from django.contrib import admin

from .models import Facilities, Availability, Reservation

# Register your models here.

admin.site.register(Facilities)
admin.site.register(Availability)
admin.site.register(Reservation)