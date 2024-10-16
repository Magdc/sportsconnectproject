from django.shortcuts import render, get_object_or_404, redirect
from facility.models import Facilities, Availability
from reservation.models import Reservation
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import User
from .forms import FacilityForm, RestrictionForm
from django.contrib import messages
from django.http import JsonResponse
from datetime import time
from django.contrib import messages


# Create your views here.
@staff_member_required
def adminsite(request):
    facilities = Facilities.objects.all()
    reservas = Reservation.objects.all()
    users = User.objects.all()

    context = {
        'facilities': facilities,
        'reservas': reservas,
        'users': users
    }

    return render(request, 'adminsite.html', context)

@staff_member_required 
def crear_espacio(request):
    if request.method == 'POST':
        form = FacilityForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()  
            return redirect('adminsite') 
    else:
        form = FacilityForm()
    return render(request, 'crear_espacio.html', {'form': form})

@staff_member_required
def restringir_acceso(request, facility_id):
    facility = get_object_or_404(Facilities, idFacility=facility_id)

    if request.method == 'POST':
        if 'time_slot' in request.POST:
            selected_date = request.POST.get('date')
            form = RestrictionForm(request.POST, facility_id=facility_id, date=selected_date)

            if form.is_valid():
                selected_time_slot = form.cleaned_data['time_slot']
                selected_date = form.cleaned_data['date']

                if selected_time_slot:
                    Availability.objects.filter(facilities_id=facility_id, date=selected_date, id=selected_time_slot).update(is_restricted=True)
                    messages.success(request, 'Acceso restringido con éxito para el horario seleccionado.')
                    return redirect('restringir_acceso', facility_id=facility_id)

        elif 'enable_time_slot' in request.POST:
            time_slot_id = request.POST.get('enable_time_slot')
            try:
                Availability.objects.filter(id=time_slot_id).update(is_restricted=False)
                messages.success(request, 'Acceso habilitado con éxito para el horario seleccionado.')
            except Availability.DoesNotExist:
                messages.error(request, 'No se pudo encontrar el horario para habilitar.')
            return redirect('restringir_acceso', facility_id=facility_id)

    else:
        form = RestrictionForm(facility_id=facility_id)

    restricted_timeslots = Availability.objects.filter(facilities_id=facility_id, is_restricted=True)

    return render(request, 'restringir_acceso.html', {'facility': facility, 'form': form, 'restricted_timeslots': restricted_timeslots})
@staff_member_required
def mostrarGraficas(request):
    return render(request, 'analiticas.html')

@staff_member_required
def eliminar_espacio(request, facility_id):
    facility = get_object_or_404(Facilities, idFacility=facility_id)
    
    if request.method == 'POST':
        facility.delete()  
        messages.success(request, 'Espacio eliminado con éxito.')
        return redirect('adminsite')  
    
    return render(request, 'eliminacion.html', {'facility': facility})

@staff_member_required
def eliminar_reservacion(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        reservation.delete()  
        messages.success(request, 'Reservación eliminada con éxito.')
        return redirect('adminsite') 
    
    return render(request, 'eliminacion_reservacion.html', {'reserva': reservation})
