from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Availability, Facilities
from datetime import time, timedelta
from django.utils import timezone

@receiver(post_save, sender=Facilities)
def assign_time_slots(sender, instance, created, **kwargs):
    if created:
        # Crear horarios desde las 5am hasta las 9pm para el día asociado
        start_hour = 5
        end_hour = 21  
        days_to_generate = 7  # Generar slots para los próximos 7 días

        for day_offset in range(days_to_generate):
            target_date = timezone.now().date() + timedelta(days=day_offset)
            for hour in range(start_hour, end_hour + 1):
                time_slot = time(hour=hour)
                
                # Verificar si el slot ya existe antes de crearlo
                Availability.objects.get_or_create(
                    facilities=instance,
                    date=target_date,
                    time_slot=time_slot
                )