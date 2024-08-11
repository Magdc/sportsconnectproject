from django.shortcuts import render
from .models import Facilities, Availability

def home(request):
    facilities = Facilities.objects.all()
    facilities_with_availability = []

    for facility in facilities:
        availability = Availability.objects.filter(facilities=facility).order_by('time_slot')
        facilities_with_availability.append({
            'facility': facility,
            'availability': availability
        })

    context = {
        'facilities_with_availability': facilities_with_availability,
    }
    return render(request, 'home.html', context)