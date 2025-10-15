from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from reservation.models import Reservation
from facility.models import Facilities
from .models import Rating, FacilityRatingStats
from .forms import RatingForm


@login_required
def create_rating(request, reservation_id):
    """
    Vista para crear una calificación asociada a una reserva completada.
    Solo el usuario que hizo la reserva puede calificarla.
    """
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Validar que el usuario actual es el dueño de la reserva
    if reservation.idUser != request.user:
        return HttpResponseForbidden("No puedes calificar una reserva que no es tuya.")
    
    # Validar que la reserva ya ocurrió (fecha + hora pasadas)
    reservation_datetime = timezone.make_aware(
        timezone.datetime.combine(reservation.date, reservation.availability.time_slot)
    )
    if reservation_datetime > timezone.now():
        messages.error(request, "Solo puedes calificar espacios después de usar tu reserva.")
        return redirect('Historial')
    
    # Verificar si ya existe una calificación para esta reserva
    if hasattr(reservation, 'rating'):
        messages.info(request, "Ya calificaste esta reserva.")
        return redirect('view_rating', rating_id=reservation.rating.id)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.facility = reservation.facilities
            rating.reservation = reservation
            rating.save()
            messages.success(request, f"¡Gracias por calificar {reservation.facilities.name}!")
            return redirect('Historial')
    else:
        form = RatingForm()
    
    context = {
        'form': form,
        'reservation': reservation,
        'facility': reservation.facilities
    }
    return render(request, 'rating/create_rating.html', context)


@login_required
def view_rating(request, rating_id):
    """Vista para ver detalles de una calificación específica"""
    rating = get_object_or_404(Rating, id=rating_id)
    
    context = {
        'rating': rating,
        'can_edit': rating.user == request.user
    }
    return render(request, 'rating/view_rating.html', context)


@login_required
def edit_rating(request, rating_id):
    """Vista para editar una calificación existente"""
    rating = get_object_or_404(Rating, id=rating_id)
    
    # Solo el autor puede editar
    if rating.user != request.user:
        return HttpResponseForbidden("No puedes editar una calificación que no es tuya.")
    
    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            messages.success(request, "Calificación actualizada correctamente.")
            return redirect('view_rating', rating_id=rating.id)
    else:
        form = RatingForm(instance=rating)
    
    context = {
        'form': form,
        'rating': rating,
        'is_edit': True
    }
    return render(request, 'rating/create_rating.html', context)


def facility_ratings(request, facility_id):
    """Vista pública para ver todas las calificaciones de un espacio"""
    facility = get_object_or_404(Facilities, idFacility=facility_id)
    ratings = Rating.objects.for_facility(facility)
    
    # Obtener estadísticas agregadas (Composite pattern)
    stats = None
    try:
        stats = FacilityRatingStats.objects.get(facility=facility)
    except FacilityRatingStats.DoesNotExist:
        pass
    
    # Si el usuario está autenticado, buscar reservas pasadas que pueda calificar
    can_rate_reservations = []
    if request.user.is_authenticated:
        from django.utils import timezone
        now = timezone.now()
        
        # Buscar reservas pasadas del usuario en esta instalación que no tengan calificación
        past_reservations = Reservation.objects.filter(
            idUser=request.user,
            facilities=facility
        ).select_related('availability')
        
        for reservation in past_reservations:
            # Verificar si la reserva ya pasó
            reservation_datetime = timezone.make_aware(
                timezone.datetime.combine(reservation.date, reservation.availability.time_slot)
            )
            
            # Si la reserva pasó y no tiene calificación, puede calificarla
            if reservation_datetime < now and not hasattr(reservation, 'rating'):
                can_rate_reservations.append(reservation)
    
    context = {
        'facility': facility,
        'ratings': ratings,
        'stats': stats,
        'can_rate_reservations': can_rate_reservations,
    }
    return render(request, 'rating/facility_ratings.html', context)


@login_required
def my_ratings(request):
    """Vista para que el usuario vea todas sus calificaciones"""
    ratings = Rating.objects.by_user(request.user)
    
    context = {
        'ratings': ratings
    }
    return render(request, 'rating/my_ratings.html', context)
