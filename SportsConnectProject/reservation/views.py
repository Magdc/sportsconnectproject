from django.shortcuts import render
from django.http import JsonResponse
from .models import Facilities, Availability, Reservation
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import timedelta
from django.utils import timezone
from datetime import datetime

#Método para mostrar la página principal
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
#Método para generar y obtener la disponibilidad de una instalación en una fecha específica
def get_availability_by_date(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        idFacility = request.POST.get('idFacility')

        # Obtener la fecha de hoy
        today = timezone.now().date()

        # Generar disponibilidad para los próximos 7 días si no existe
        facility = Facilities.objects.get(idFacility=idFacility)
        for i in range(7):
            date_to_check = today + timedelta(days=i)
            for time_slot in Availability.generate_time_slots(self=facility):  # Utiliza el método del modelo
                # Crear disponibilidad si no existe ya
                Availability.objects.get_or_create(facilities=facility, date=date_to_check, time_slot=time_slot)

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

#Método para gestionar reservas
def reservate(request):
    if request.method == 'POST':
        idFacility = request.POST.get('facilities_id')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')

        if time_slot and len(time_slot) == 5:
            time_slot += ':00'

        try:
            # Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'Querido usuario, por favor inicie sesión para reservar.'})

            # Límite de reservas por semana
            limit_reservations_per_week = 3

            # Calcular el inicio de la semana (por defecto el lunes)
            start_of_week = timezone.now().date() - timedelta(days=timezone.now().date().weekday())

            # Contar cuántas reservas ha hecho el usuario esta semana
            user_reservations_this_week = Reservation.objects.filter(
                idUser=request.user,
                date__gte=start_of_week
            ).count()

            if user_reservations_this_week >= limit_reservations_per_week:
                return JsonResponse({'success': False, 'error': f'No puedes tener mas de {limit_reservations_per_week} reservas activas.'})

            # Obtener la instalación usando el campo 'idFacility'
            facility = Facilities.objects.get(idFacility=idFacility)

            # Intentar obtener la disponibilidad basada en la instalación, fecha y hora seleccionada
            availability = Availability.objects.get(facilities=facility, date=date, time_slot=time_slot)

            # Verificar si ya existe una reserva para esa disponibilidad
            if Reservation.objects.filter(availability=availability).exists():
                return JsonResponse({'success': False, 'error': 'Lo sentimos! Este horario ya ha sido reservado.'})
            else:
                # Crear la nueva reserva asociada al usuario autenticado
                new_reservation = Reservation.objects.create(
                    idUser=request.user,
                    facilities=facility,
                    availability=availability,
                    date=date
                )

                # Retornar el id de la reserva recién creada
                return JsonResponse({'success': True, 'reservation_id': new_reservation.id})

        except Facilities.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Instalación no encontrada.'})

        except Availability.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Disponibilidad no encontrada para la fecha y hora seleccionadas.'})

        except Exception as e:
            # Capturar cualquier otro error no previsto y devolver detalles
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'error': 'Requerimiento inválido'}, status=400)

#Método para eliminar una reserva
def delete_reservation(request):
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')

        try:
            # Obtener la reserva basada en el ID
            reservation = Reservation.objects.get(id=reservation_id)

            # Eliminar la reserva
            reservation.delete()

            return JsonResponse({'success': True, 'message': 'Reserva eliminada correctamente.'})

        except Reservation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Reserva no encontrada.'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

# Método para mostrar las reservas
def historial(request):
    user = request.user.idUser
    reservas=Reservation.objects.filter(idUser=user)
    fechahoy = datetime.now()
    activas = reservas.filter(date__gte=fechahoy)
    vencidas= reservas.filter(date__lt=fechahoy)
    for i in reservas:
        print(reservas)
    return render(request, 'historial.html',{"activas":activas,"vencidas":vencidas})

#metodo de prueba para eliminar la reserva desde el historial sin pedir ID de reserva
def delete_reservation_historial(request):
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')

        if not reservation_id:
            return JsonResponse({'success': False, 'error': 'ID de reserva no proporcionado.'})

        try:
            # Verificar si la reserva pertenece al usuario actual
            reservation = Reservation.objects.get(id=reservation_id, idUser=request.user)

            # Eliminar la reserva si pertenece al usuario
            reservation.delete()

            return JsonResponse({'success': True, 'message': 'Reserva eliminada correctamente.'})

        except Reservation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Reserva no encontrada o no pertenece al usuario.'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

