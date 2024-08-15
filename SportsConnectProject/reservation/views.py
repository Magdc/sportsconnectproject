from django.shortcuts import render
from django.http import JsonResponse
from .models import Facilities, Availability, Reservation
from django.views.decorators.csrf import csrf_exempt
import json

def home(request):
    facilities = Facilities.objects.all()
    facilities_with_availability = []

    for facility in facilities:
        availability = Availability.objects.filter(facilities=facility).order_by('time_slot')
        facilities_with_availability.append({
            'facility': facility,
            'availability': availability
        })

    for facility_info in facilities_with_availability:
        print(f"Facility: {facility_info['facility'].name}")
        for slot in facility_info['availability']:
            print(f"Time Slot: {slot.time_slot}")

    context = {
        'facilities_with_availability': facilities_with_availability,
    }
    return render(request, 'home.html', context)

@csrf_exempt
def get_availability_by_date(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        idFacility = request.POST.get('idFacility')

        # Filtrar disponibilidad para la fecha seleccionada y la instalación específica
        availability = Availability.objects.filter(facilities_id=idFacility, date=selected_date).order_by('time_slot')

        # Obtener los horarios ya reservados para esa fecha y esa instalación
        reserved_slots = Reservation.objects.filter(availability__facilities_id=idFacility, date=selected_date).values_list('availability__time_slot', flat=True)

        # Excluir los horarios ya reservados de la lista de disponibilidad
        available_slots = availability.exclude(time_slot__in=reserved_slots).distinct()

        # Crear una lista de la disponibilidad restante sin duplicados
        availability_list = [{'id': slot.id, 'time_slot': slot.time_slot.strftime('%H:%M')} for slot in available_slots]

        return JsonResponse({'availability': availability_list})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def reservate(request):
    if request.method == 'POST':
        idFacility = request.POST.get('facilities_id')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')

        if time_slot and len(time_slot) == 5:  # Verificar que el formato del tiempo sea HH:MM
            time_slot += ':00'  # Convertir a HH:MM:00

        try:
            # Intentar obtener la disponibilidad basada en la instalación, fecha y hora seleccionada
            availability = Availability.objects.get(facilities_id=idFacility, date=date, time_slot=time_slot)

            # Verificar si ya existe una reserva para esa disponibilidad
            if Reservation.objects.filter(availability=availability).exists():
                return JsonResponse({'success': False, 'error': 'This schedule is already reserved'})
            else:
                # Crear la nueva reserva
                new_reservation = Reservation.objects.create(facilities_id=idFacility, availability=availability, date=date)
                return JsonResponse({'success': True, 'reservation_id': new_reservation.id})
        
        except Availability.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Availability not found.'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def delete_reservation(request):
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')

        try:
            # obtener reserva basada en el ID
            reservation = Reservation.objects.get(id=reservation_id)

            # eliminar la reserva
            reservation.delete()

            return JsonResponse({'success': True, 'message': 'Reservation deleted successfully'})

        except Reservation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Reservation not found'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

