"""
Strategy Pattern: Define diferentes algoritmos para calcular el rating agregado de un espacio deportivo.
Permite cambiar fácilmente el método de cálculo sin modificar el código cliente.
"""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Dict, Any


class RatingCalculationStrategy(ABC):
    """Interfaz abstracta para estrategias de cálculo de rating"""
    
    @abstractmethod
    def calculate(self, ratings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula el rating agregado basado en una estrategia específica.
        
        Args:
            ratings_data: Lista de diccionarios con información de ratings
                         [{'stars': int, 'created_at': datetime, ...}, ...]
        
        Returns:
            Dict con 'average_rating' y 'total_ratings'
        """
        pass


class SimpleAverageStrategy(RatingCalculationStrategy):
    """Estrategia simple: promedio aritmético de todas las calificaciones"""
    
    def calculate(self, ratings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not ratings_data:
            return {'average_rating': Decimal('0.00'), 'total_ratings': 0}
        
        total = sum(rating['stars'] for rating in ratings_data)
        count = len(ratings_data)
        average = Decimal(total) / Decimal(count)
        
        return {
            'average_rating': round(average, 2),
            'total_ratings': count
        }


class WeightedRecentStrategy(RatingCalculationStrategy):
    """
    Estrategia ponderada: da más peso a calificaciones recientes.
    Las calificaciones más nuevas tienen mayor impacto en el promedio.
    """
    
    def __init__(self, decay_factor: float = 0.9):
        """
        Args:
            decay_factor: Factor de decaimiento (0-1). Valores cercanos a 1 
                         dan más peso a ratings recientes.
        """
        self.decay_factor = decay_factor
    
    def calculate(self, ratings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not ratings_data:
            return {'average_rating': Decimal('0.00'), 'total_ratings': 0}
        
        # Ordenar por fecha (más recientes primero)
        sorted_ratings = sorted(
            ratings_data, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )
        
        weighted_sum = Decimal('0')
        weight_total = Decimal('0')
        
        for i, rating in enumerate(sorted_ratings):
            weight = Decimal(str(self.decay_factor ** i))
            weighted_sum += Decimal(rating['stars']) * weight
            weight_total += weight
        
        average = weighted_sum / weight_total if weight_total > 0 else Decimal('0')
        
        return {
            'average_rating': round(average, 2),
            'total_ratings': len(ratings_data)
        }


class BayesianAverageStrategy(RatingCalculationStrategy):
    """
    Estrategia Bayesiana: evita que espacios con pocas calificaciones 
    muy altas dominen el ranking. Pondera con un promedio global.
    """
    
    def __init__(self, global_average: float = 3.5, confidence: int = 10):
        """
        Args:
            global_average: Promedio global del sistema (prior)
            confidence: Número de "votos virtuales" para el prior
        """
        self.global_average = Decimal(str(global_average))
        self.confidence = confidence
    
    def calculate(self, ratings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not ratings_data:
            return {'average_rating': self.global_average, 'total_ratings': 0}
        
        total = sum(rating['stars'] for rating in ratings_data)
        count = len(ratings_data)
        
        # Bayesian average: (C*m + Σx) / (C + n)
        # C = confidence, m = global_average, Σx = sum, n = count
        numerator = (self.confidence * self.global_average) + Decimal(total)
        denominator = self.confidence + count
        average = numerator / Decimal(denominator)
        
        return {
            'average_rating': round(average, 2),
            'total_ratings': count
        }


class RatingCalculatorFactory:
    """
    Factory Pattern: Crea instancias de estrategias de cálculo de rating.
    Centraliza la lógica de creación y permite añadir nuevas estrategias fácilmente.
    """
    
    _strategies = {
        'simple': SimpleAverageStrategy,
        'weighted': WeightedRecentStrategy,
        'bayesian': BayesianAverageStrategy,
    }
    
    @classmethod
    def create(cls, strategy_name: str = 'simple', **kwargs) -> RatingCalculationStrategy:
        """
        Crea una estrategia de cálculo de rating.
        
        Args:
            strategy_name: Nombre de la estrategia ('simple', 'weighted', 'bayesian')
            **kwargs: Parámetros específicos para la estrategia
        
        Returns:
            Instancia de RatingCalculationStrategy
        
        Raises:
            ValueError: Si el nombre de estrategia no es válido
        """
        strategy_class = cls._strategies.get(strategy_name.lower())
        if not strategy_class:
            raise ValueError(
                f"Estrategia '{strategy_name}' no válida. "
                f"Opciones: {list(cls._strategies.keys())}"
            )
        
        return strategy_class(**kwargs)
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """Permite registrar nuevas estrategias dinámicamente"""
        cls._strategies[name.lower()] = strategy_class
