from django.shortcuts import render, get_object_or_404, redirect
from facility.models import Facilities, Availability
from reservation.models import Reservation
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import User


# Create your views here.
@staff_member_required
def adminsite(request):
    # Obtener todos los espacios
    facilities = Facilities.objects.all()

    # Obtener todas las reservas
    reservas = Reservation.objects.all()

    # Obtener todos los usuarios del modelo personalizado
    users = User.objects.all()

    # Pasar los datos al contexto
    context = {
        'facilities': facilities,
        'reservas': reservas,
        'users': users
    }

    return render(request, 'adminsite.html', context)

def crear_espacio(request):
    # Lógica para crear un nuevo espacio
    pass

def restringir_acceso(request, facility_id):
    facility = get_object_or_404(Facilities, id=facility_id)
    # Lógica para restringir acceso
    pass