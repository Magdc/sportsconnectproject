from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from .models import Facilities
def home(request):

    facilities = Facilities.objects.all()

    return render(request, 'home.html', {'facilities': facilities})