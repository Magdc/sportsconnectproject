from django.shortcuts import render
from django.http import JsonResponse
from .models import Facilities, Availability, Reservation
from django.views.decorators.csrf import csrf_exempt

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
        idFacility = request.POST.get('facilities_id')
        print(f"Selected Date: {selected_date}, Facility ID: {idFacility}")

        availability = Availability.objects.filter( facilities_id=idFacility, date=selected_date ).order_by('time_slot')

        availability_list = [{'id': slot.id, 'time_slot': slot.time_slot.strftime('%H:%M')} for slot in availability]
        print("Availability List:", availability_list)
    
        return JsonResponse({'availability': availability_list})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def reservate(request):
    if request.method == 'POST':
        idFacility = request.POST.get('idFacility')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')

        try:
            # Ahora usando get para obtener una sola instancia
            availability = Availability.objects.get(facilities_id=idFacility, date=date, time_slot=time_slot)

            # Verificamos si ya existe una reserva para esa disponibilidad
            if Reservation.objects.filter(availability=availability).exists():
                return JsonResponse({'success': False, 'Error': 'This Schedule is already reserved'})
            else:
                # Crear la nueva reserva
                new_reservation = Reservation.objects.create(facilities_id=idFacility, availability=availability, date=date)
                return JsonResponse({'success': True})
        
        except Availability.DoesNotExist:
            return JsonResponse({'success': False, 'Error': 'Availability not found.'})
        
def delete_reservation(request):
    if request.method == 'POST':
        idReservation = request.POST.get('idReservation')
        try:
            reservation = Reservation.objects.get(id=idReservation)
            reservation.delete()
            return JsonResponse({'success': True})
        except Reservation.DoesNotExist:
            return JsonResponse({'success': False, 'Error': 'Reservation not found.'})
    

