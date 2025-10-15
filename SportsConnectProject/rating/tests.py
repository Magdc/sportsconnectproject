from django.test import TestCase
from decimal import Decimal
from rating.rating_calculator import (
    SimpleAverageStrategy,
    WeightedRecentStrategy,
    BayesianAverageStrategy,
    RatingCalculatorFactory
)
from datetime import datetime


class RatingCalculationStrategyTests(TestCase):
    """Tests para los patrones Strategy implementados en el sistema de calificaciones"""
    
    def setUp(self):
        """Datos de prueba comunes"""
        self.sample_ratings = [
            {'stars': 5, 'created_at': datetime(2025, 10, 1)},
            {'stars': 4, 'created_at': datetime(2025, 10, 5)},
            {'stars': 3, 'created_at': datetime(2025, 10, 10)},
        ]
    
    def test_simple_average_strategy(self):
        """Test para SimpleAverageStrategy"""
        strategy = SimpleAverageStrategy()
        result = strategy.calculate(self.sample_ratings)
        
        # (5 + 4 + 3) / 3 = 4.0
        self.assertEqual(result['average_rating'], Decimal('4.00'))
        self.assertEqual(result['total_ratings'], 3)
    
    def test_simple_average_empty_ratings(self):
        """Test para SimpleAverageStrategy con lista vacía"""
        strategy = SimpleAverageStrategy()
        result = strategy.calculate([])
        
        self.assertEqual(result['average_rating'], Decimal('0.00'))
        self.assertEqual(result['total_ratings'], 0)
    
    def test_weighted_recent_strategy(self):
        """Test para WeightedRecentStrategy"""
        strategy = WeightedRecentStrategy(decay_factor=0.9)
        result = strategy.calculate(self.sample_ratings)
        
        # Las calificaciones más recientes tienen más peso
        self.assertGreater(result['average_rating'], Decimal('0'))
        self.assertEqual(result['total_ratings'], 3)
    
    def test_bayesian_average_strategy(self):
        """Test para BayesianAverageStrategy"""
        strategy = BayesianAverageStrategy(global_average=3.5, confidence=10)
        result = strategy.calculate(self.sample_ratings)
        
        # Con pocos ratings, se acerca más al promedio global
        self.assertGreater(result['average_rating'], Decimal('0'))
        self.assertEqual(result['total_ratings'], 3)
    
    def test_factory_creates_simple_strategy(self):
        """Test para Factory creando SimpleAverageStrategy"""
        strategy = RatingCalculatorFactory.create('simple')
        self.assertIsInstance(strategy, SimpleAverageStrategy)
    
    def test_factory_creates_weighted_strategy(self):
        """Test para Factory creando WeightedRecentStrategy"""
        strategy = RatingCalculatorFactory.create('weighted', decay_factor=0.8)
        self.assertIsInstance(strategy, WeightedRecentStrategy)
    
    def test_factory_creates_bayesian_strategy(self):
        """Test para Factory creando BayesianAverageStrategy"""
        strategy = RatingCalculatorFactory.create('bayesian')
        self.assertIsInstance(strategy, BayesianAverageStrategy)
    
    def test_factory_invalid_strategy_raises_error(self):
        """Test para Factory con estrategia inválida"""
        with self.assertRaises(ValueError):
            RatingCalculatorFactory.create('invalid_strategy')
