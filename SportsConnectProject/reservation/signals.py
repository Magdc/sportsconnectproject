from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Availability, Facilities
from datetime import time

@receiver(post_save, sender=Availability)
def assign_time_slots(sender, instance, created, **kwargs):
    if created:
        # Crear horarios desde las 5am hasta las 5pm para el día asociado
        start_hour = 5
        end_hour = 17  

        for hour in range(start_hour, end_hour + 1):
            time_slot = time(hour=hour)
            # Crear una nueva entrada de Availability para cada franja horaria
            Availability.objects.get_or_create(
                facilities=instance.facilities,
                day=instance.day,
                time_slot=time_slot
            )