import os
import base64
from reservation.notification_services import NotificationService, ConsoleNotificationService, EmailNotificationService
from .notification_factory import get_notification_service
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
# Import models from the correct apps
from facility.models import Facilities, Availability
from reservation.models import Reservation, WaitList
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from datetime import timedelta, datetime
from django.utils import timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from email.mime.text import MIMEText
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import User
from django.db.models import Q
from django.contrib import messages

#Método para mostrar la página principal
def home(request):
    query = request.GET.get('search', '')  
    facilities = Facilities.objects.all()

    if query:
        facilities = facilities.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    facilities_with_availability = []

    for facility in facilities:
        availability = Availability.objects.filter(facilities=facility).order_by('time_slot')
        facilities_with_availability.append({
            'facility': facility,
            'availability': availability
        })

    context = {
        'facilities_with_availability': facilities_with_availability,
        'search_query': query,  # Pasar el término de búsqueda al contexto
    }
    return render(request, 'home.html', context)

#Método para generar y obtener la disponibilidad de una instalación en una fecha específica
@csrf_exempt
def get_availability_by_date(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        idFacility = request.POST.get('idFacility')
        today = timezone.now().date()

        # Generar disponibilidad para los próximos 7 días si no existe
        facility = Facilities.objects.get(idFacility=idFacility)
        for i in range(7):
            date_to_check = today + timedelta(days=i)
            # generate_time_slots is an instance method on Availability; call it on a temporary instance
            for time_slot in Availability().generate_time_slots():
                # Crear disponibilidad si no existe ya
                Availability.objects.get_or_create(facilities=facility, date=date_to_check, time_slot=time_slot)

        # Filtrar disponibilidad para la fecha seleccionada
        availability = Availability.objects.filter(
            facilities_id=idFacility, 
            date=selected_date,
            is_restricted=False  
        ).order_by('time_slot')

        # Obtener los horarios
        reserved_slots = Reservation.objects.filter(
            availability__facilities_id=idFacility, 
            date=selected_date
        ).values_list('availability__time_slot', flat=True)

        # Excluir los horarios ya reservados
        available_slots = availability.exclude(time_slot__in=reserved_slots).distinct()

        # Crear una lista de la disponibilidad
        availability_list = [{'id': slot.id, 'time_slot': slot.time_slot.strftime('%H:%M')} for slot in available_slots]

        return JsonResponse({'availability': availability_list})

    return JsonResponse({'error': 'Invalid request'}, status=400)

#Método para gestionar reservas
@login_required
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
                return JsonResponse({'success': False, 'error': f'No puedes tener más de {limit_reservations_per_week} reservas activas.'})

            # Obtener la instalación usando el campo 'idFacility'
            facility = Facilities.objects.get(idFacility=idFacility)

            # Intentar obtener la disponibilidad basada en la instalación, fecha y hora seleccionada
            availability = Availability.objects.get(facilities=facility, date=date, time_slot=time_slot)

            # Verificar si ya existe una reserva para esa disponibilidad
            if Reservation.objects.filter(availability=availability).exists():
                return JsonResponse({'success': False, 'error': 'Lo sentimos, este horario ya ha sido reservado.'})
            else:
                new_reservation = Reservation.objects.create(idUser=request.user,facilities=facility,availability=availability,date=date)
                reserva_confirmacion(request,request.user.email, facility.name,new_reservation.date,availability.time_slot)
                return JsonResponse({'success': True, 'reservation_id': new_reservation.id})

        except Facilities.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Instalación no encontrada.'})

        except Availability.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Disponibilidad no encontrada para la fecha y hora seleccionadas.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'error': 'Requerimiento inválido'}, status=400)


#Método para eliminar una reserva
@login_required
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
@login_required
def historial(request):
    user = request.user.idUser
    reservas=Reservation.objects.filter(idUser=user)
    fechahoy = datetime.now()
    activas = reservas.filter(date__gte=fechahoy)
    vencidas= reservas.filter(date__lt=fechahoy)
    return render(request, 'historial.html',{"activas":activas,"vencidas":vencidas})

# Método de prueba para eliminar la reserva desde el historial sin pedir ID de reserva
@login_required
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

# Cargar variables del archivo .env
load_dotenv()

# Scopes requeridos (proteger contra variable de entorno ausente)
_SCOPES_ENV = os.getenv('GOOGLE_SCOPES')
SCOPES = _SCOPES_ENV.split(',') if _SCOPES_ENV else []

def gmail_authenticate():
    # Leer variables de entorno necesarias
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    access_token = os.getenv('GOOGLE_ACCESS_TOKEN')
    token_uri = os.getenv('GOOGLE_TOKEN_URI')

    # Si faltan datos esenciales no intentamos autenticar con la API de Gmail
    if not (refresh_token and token_uri and client_id and client_secret):
        return None

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )

    try:
        if creds.expired or not creds.valid:
            creds.refresh(Request())
    except Exception:
        # No se pudo refrescar; devolver None para que el llamador lo maneje
        return None

    return creds

def send_email(user_email, subject, message):
    creds = gmail_authenticate()
    if not creds:
        # No hay configuración OAuth completa; no intentar enviar el correo
        # En desarrollo se puede usar el backend de consola (EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend')
        return "No se envió el correo: Google OAuth no está configurado correctamente."

    try:
        service = build('gmail', 'v1', credentials=creds)

        # Crear el mensaje MIME
        message_mime = MIMEText(message)
        message_mime['to'] = user_email
        message_mime['subject'] = subject
        raw = base64.urlsafe_b64encode(message_mime.as_bytes()).decode()

        # Enviar el correo
        sent_message = service.users().messages().send(userId="me", body={'raw': raw}).execute()
        return f"Correo enviado correctamente: ID {sent_message.get('id')}"
    except Exception as e:
        # No propagamos la excepción: devolvemos un mensaje para registro/feedback
        return f"Error enviando el correo: {str(e)}"

def reserva_confirmacion(request, user_email, facility_name, reservation_date, time_slot, notification_service=None):
    subject = "Confirmación de reserva en EAFIT"
    message = f"""
    Estimado {request.user.first_name},

    Su reserva ha sido realizada con éxito.

    Detalles de la reserva:
    - Espacio reservado: {facility_name}
    - Fecha: {reservation_date}  
    - Hora: {time_slot}
    
    ¡Gracias por usar nuestro servicio!

    Atentamente,
    El equipo de SportsConnect
    """
    if notification_service is None:
        # Strategy + Factory: selecciona la implementación adecuada según configuración/entorno
        notification_service = get_notification_service(email_sender=send_email)
    return notification_service.send(user_email, subject, message)

@login_required
def editarReserva(request, reserva_id):
    user = request.user.idUser
    # Buscar la reserva específica
    try:
        reserva = Reservation.objects.get(id=reserva_id, idUser=user)
    except Reservation.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'Reserva no encontrada.'})

    # Obtener los horarios disponibles para la fecha y espacio de la reserva
    horarios_disponibles = Availability.objects.filter(date=reserva.availability.date, facilities=reserva.facilities,is_restricted=False).order_by('time_slot')
    reserved_slots = Reservation.objects.filter(availability__facilities_id=reserva.facilities,date=reserva.availability.date).values_list('availability__time_slot', flat=True)
    available_slots = horarios_disponibles.exclude(time_slot__in=reserved_slots).distinct()


    if request.method == 'POST':      
        # Obtener el nuevo horario seleccionado del formulario
        nuevo_horario_id = request.POST.get('time_slot')
        try:
            nuevo_horario = Availability.objects.get(id=nuevo_horario_id)
        except Availability.DoesNotExist:
            return render(request, 'error.html', {'mensaje': 'Horario no válido.'})

        # Actualizar la reserva con el nuevo horario
        reserva.availability = nuevo_horario
        reserva.save()

        # Puedes redirigir a una página de éxito o mostrar un mensaje
        return JsonResponse({'success': True})

    # Si es una solicitud GET, renderizar el formulario con los horarios disponibles
    return render(request, 'editar.html', {
        'reserva': reserva,
        'horarios_disponibles': available_slots
    })
    
@login_required
def add_to_waitlist(request, facility_id):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        user = request.user
        date_str = request.POST.get('date') 
        facility = get_object_or_404(Facilities, pk=facility_id)

        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()  
            except ValueError:
                messages.error(request, "Formato de fecha inválido.")
                return redirect('home')

            if date >= datetime.now().date():
                new_waitlist_entry = WaitList(user=user, facilities=facility, date=date)
                new_waitlist_entry.save()

                WaitList_confirmacion(request, user.email, facility.name, date=date)
                messages.success(request, "Añadido a la lista de espera exitosamente.")
                return render(request, 'add_to_waitlist.html', {'facility': facility})
            else:
                messages.error(request, "No puedes añadirte a la lista de espera para fechas pasadas.")

            return redirect('home')
        else:
            messages.error(request, "No se proporcionó una fecha.")
            return redirect('home')

def WaitList_confirmacion(request, user_email, facility_name, date, notification_service=None):
    subject = "SUSCRIPCIÓN A LISTA DE ESPERA EAFIT"
    message = f"""
    Estimado {request.user.first_name},

    Ha sido incluido en la Waitlist.

    Detalles del espacio que esta esperando:
    - Espacio esperado: {facility_name}
    - Fecha esperada: {date}  
    
    ¡Gracias por usar nuestro servicio!

    Atentamente,
    El equipo de SportsConnect
    """
    if notification_service is None:
        # Strategy + Factory: selecciona la implementación adecuada según configuración/entorno
        notification_service = get_notification_service(email_sender=send_email)
    return notification_service.send(user_email, subject, message)
