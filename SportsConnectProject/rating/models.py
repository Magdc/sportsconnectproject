from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from facility.models import Facilities
from reservation.models import Reservation


class RatingManager(models.Manager):
    """Manager personalizado para consultas comunes de Rating (Repository-like pattern)"""
    
    def for_facility(self, facility):
        """Obtiene todas las calificaciones para una instalación específica"""
        return self.get_queryset().filter(facility=facility)
    
    def average_for_facility(self, facility):
        """Calcula el promedio de calificaciones para una instalación"""
        result = self.for_facility(facility).aggregate(
            avg=models.Avg('stars'),
            count=models.Count('id')
        )
        return result
    
    def by_user(self, user):
        """Obtiene todas las calificaciones de un usuario"""
        return self.get_queryset().filter(user=user)


class Rating(models.Model):
    """
    Modelo para almacenar calificaciones de usuarios sobre espacios deportivos.
    Soporta el patrón Composite al agregar múltiples ratings en estadísticas.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    facility = models.ForeignKey(Facilities, on_delete=models.CASCADE, related_name='ratings')
    reservation = models.OneToOneField(
        Reservation, 
        on_delete=models.CASCADE, 
        related_name='rating',
        null=True,
        blank=True,
        help_text="Reserva asociada a esta calificación"
    )
    stars = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5 estrellas"
    )
    comment = models.TextField(blank=True, help_text="Comentario opcional del usuario")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = RatingManager()
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'reservation']  # Un usuario solo puede calificar una reserva una vez
    
    def __str__(self):
        return f"{self.user.email} - {self.facility.name}: {self.stars}★"


class FacilityRatingStats(models.Model):
    """
    Modelo que implementa el patrón Composite: agrega múltiples Rating 
    en estadísticas consolidadas para cada Facility.
    Se actualiza automáticamente mediante signals (Observer pattern).
    """
    facility = models.OneToOneField(
        Facilities, 
        on_delete=models.CASCADE, 
        related_name='rating_stats',
        primary_key=True
    )
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0,
        help_text="Promedio de calificaciones (Composite)"
    )
    total_ratings = models.IntegerField(
        default=0,
        help_text="Total de calificaciones recibidas"
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Estadísticas de Calificación"
        verbose_name_plural = "Estadísticas de Calificaciones"
    
    def __str__(self):
        return f"{self.facility.name}: {self.average_rating}★ ({self.total_ratings} ratings)"
