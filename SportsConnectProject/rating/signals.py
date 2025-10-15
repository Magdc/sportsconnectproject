"""
Observer Pattern usando Django Signals: cuando se crea, actualiza o elimina un Rating,
se recalculan automáticamente las estadísticas agregadas (FacilityRatingStats).
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Rating, FacilityRatingStats
from .rating_calculator import RatingCalculatorFactory
import os


def update_facility_stats(facility):
    """
    Actualiza las estadísticas de rating para una instalación usando la estrategia
    de cálculo configurada en variables de entorno (o 'simple' por defecto).
    """
    # Obtener todas las calificaciones de la instalación
    ratings = Rating.objects.for_facility(facility).values('stars', 'created_at')
    ratings_list = list(ratings)
    
    # Seleccionar estrategia de cálculo desde configuración
    strategy_name = os.getenv('RATING_CALCULATION_STRATEGY', 'simple')
    calculator = RatingCalculatorFactory.create(strategy_name)
    
    # Calcular estadísticas usando la estrategia seleccionada
    stats = calculator.calculate(ratings_list)
    
    # Actualizar o crear el registro de estadísticas (Composite pattern)
    FacilityRatingStats.objects.update_or_create(
        facility=facility,
        defaults={
            'average_rating': stats['average_rating'],
            'total_ratings': stats['total_ratings']
        }
    )


@receiver(post_save, sender=Rating)
def rating_saved(sender, instance: Rating, created, **kwargs):
    """
    Observer: cuando se crea o actualiza un Rating, recalcula las estadísticas
    agregadas de la instalación correspondiente.
    """
    update_facility_stats(instance.facility)


@receiver(post_delete, sender=Rating)
def rating_deleted(sender, instance: Rating, **kwargs):
    """
    Observer: cuando se elimina un Rating, recalcula las estadísticas
    agregadas de la instalación correspondiente.
    """
    update_facility_stats(instance.facility)
