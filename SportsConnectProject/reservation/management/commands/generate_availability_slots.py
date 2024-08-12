from django.core.management.base import BaseCommand
from reservation.models import Availability
from datetime import time

class Command(BaseCommand):
    help = 'Assign time slots to existing Availability entries'

    def handle(self, *args, **kwargs):
        # Iterar sobre todas las entradas existentes en Availability
        availabilities = Availability.objects.all()

        for availability in availabilities:
            # Verificar si los horarios ya existen para evitar duplicados
            existing_slots = Availability.objects.filter(
                facilities=availability.facilities,
                date=availability.date
            ).values_list('time_slot', flat=True)

            start_hour = 5
            end_hour = 21  # 5pm in 24-hour format

            # Crear los horarios faltantes
            for hour in range(start_hour, end_hour + 1):
                time_slot = time(hour=hour)
                if time_slot not in existing_slots:
                    Availability.objects.create(
                        facilities=availability.facilities,
                        date=availability.date,
                        time_slot=time_slot
                    )
        
        self.stdout.write(self.style.SUCCESS('Successfully assigned time slots to all existing Availability entries'))