# Sistema de Calificaciones - Funcionalidad BONO

## Descripción
Sistema completo de calificaciones que permite a los usuarios evaluar los espacios deportivos después de usarlos. Los usuarios pueden calificar de 1 a 5 estrellas y dejar comentarios opcionales.

## Patrones de Diseño Aplicados

### 1. Strategy Pattern (rating_calculator.py)
**Problema**: Necesitamos diferentes algoritmos para calcular el rating agregado de un espacio.

**Solución**: Implementamos tres estrategias intercambiables:
- `SimpleAverageStrategy`: Promedio aritmético simple
- `WeightedRecentStrategy`: Da más peso a calificaciones recientes
- `BayesianAverageStrategy`: Evita que espacios con pocas calificaciones altas dominen el ranking

**Beneficio**: Podemos cambiar el algoritmo de cálculo sin modificar el código cliente. Se configura con la variable de entorno `RATING_CALCULATION_STRATEGY`.

```python

strategy = RatingCalculatorFactory.create('weighted')
stats = strategy.calculate(ratings_data)
```

### 2. Factory Pattern (RatingCalculatorFactory)
**Problema**: Necesitamos centralizar la creación de estrategias de cálculo.

**Solución**: Factory que crea instancias según nombre:

```python
calculator = RatingCalculatorFactory.create('simple')

calculator = RatingCalculatorFactory.create('weighted', decay_factor=0.9)
```

### 3. Repository Pattern (RatingManager)
**Problema**: Consultas comunes sobre calificaciones repetidas en múltiples lugares.

**Solución**: Manager personalizado con métodos específicos:

```python
Rating.objects.for_facility(facility)  # Todas las calificaciones de un espacio
Rating.objects.average_for_facility(facility)  # Promedio y conteo
Rating.objects.by_user(user)  # Calificaciones de un usuario
```

### 4. Composite Pattern (FacilityRatingStats)
**Problema**: Necesitamos agregar múltiples Rating individuales en estadísticas consolidadas.

**Solución**: Modelo `FacilityRatingStats` que representa la composición de múltiples ratings:
- `average_rating`: Promedio calculado
- `total_ratings`: Conteo total
- Se actualiza automáticamente vía signals


### 5. Observer Pattern (signals.py)
**Problema**: Cuando se crea/actualiza/elimina un Rating, las estadísticas deben actualizarse.

**Solución**: Signals de Django (`post_save`, `post_delete`) escuchan cambios en Rating y actualizan `FacilityRatingStats`:

```python
@receiver(post_save, sender=Rating)
def rating_saved(sender, instance, created, **kwargs):
    update_facility_stats(instance.facility)
```

## Arquitectura

```
rating/
├── models.py              # Rating, FacilityRatingStats, RatingManager
├── rating_calculator.py   # Estrategias de cálculo (Strategy + Factory)
├── signals.py             # Observers para actualizar stats
├── views.py               # Vistas CRUD para calificaciones
├── forms.py               # RatingForm con RadioSelect para estrellas
├── urls.py                # URLs del módulo
├── admin.py               # Admin interface
├── tests.py               # Tests para Strategy y Factory
└── templates/rating/      # Templates HTML
```

## Integración con el Sistema Existente

### 1. Historial de Reservas
- Botón "Calificar este espacio" en reservas pasadas
- Link "Ver mi calificación" si ya existe

### 2. Home de Espacios
- Muestra rating promedio con estrellas
- Link "Ver reseñas" para ver todas las calificaciones

### 3. Flujo de Usuario
1. Usuario completa su reserva
2. En Historial, ve la reserva pasada con botón "Calificar"
3. Crea calificación (1-5 estrellas + comentario opcional)
4. Signal actualiza automáticamente `FacilityRatingStats`
5. Rating aparece en página del espacio
6. Usuario puede editar su calificación

## Configuración

### Variables de Entorno (.env)
```env
# Estrategia de cálculo de rating: 'simple', 'weighted', 'bayesian'
RATING_CALCULATION_STRATEGY=simple
```

### Migraciones
```powershell
python manage.py makemigrations rating
python manage.py migrate
```

## Validaciones Implementadas

1. **Ownership**: Solo el usuario que hizo la reserva puede calificarla
2. **Timing**: Solo se puede calificar después de que la reserva ocurrió
3. **Uniqueness**: Un usuario solo puede calificar una reserva una vez (unique_together)
4. **Range**: Estrellas entre 1-5 (validators)
5. **Edit Permission**: Solo el autor puede editar su calificación

## Diagrama de Flujo

```
Usuario completa reserva
         ↓
Ve botón "Calificar" en Historial
         ↓
Crea Rating (1-5★ + comentario)
         ↓
post_save Signal → update_facility_stats()
         ↓
Factory crea Strategy según config
         ↓
Strategy.calculate() → nuevo promedio
         ↓
FacilityRatingStats actualizado
         ↓
Rating visible en Home y página del espacio
```
