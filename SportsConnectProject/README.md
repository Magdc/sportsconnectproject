# SportsConnectProject

Proyecto Django para gestión de reservas de espacios deportivos.

## Requisitos
- Python 3.11+
- pip

## Configuración inicial
1. Clonar el repositorio
2. Crear y activar un entorno virtual (opcional pero recomendado)
3. Instalar dependencias
4. Configurar variables de entorno (.env)
5. Ejecutar migraciones y crear superusuario
6. Ejecutar el servidor de desarrollo

### Pasos rápidos (Windows PowerShell)
```powershell
# 1) Clonar
# git clone <URL_DEL_REPO>
# cd SportsConnectProject

# 2) (Opcional) Crear venv
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# 3) Instalar dependencias
pip install -r requirements.txt

# 4) Crear archivo .env (en la raíz del proyecto)
@"
USE_EMAIL_NOTIFICATIONS=false
RATING_CALCULATION_STRATEGY=simple
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
GOOGLE_ACCESS_TOKEN=
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_SCOPES=https://www.googleapis.com/auth/gmail.send
"@ | Out-File -FilePath .env -Encoding utf8

# 5) Migraciones y superusuario
python manage.py migrate
python manage.py createsuperuser

# 6) Correr servidor
python manage.py runserver
```

## Variables de entorno
- USE_EMAIL_NOTIFICATIONS: true/false para habilitar envío real de emails.
- RATING_CALCULATION_STRATEGY: Estrategia de cálculo de ratings ('simple', 'weighted', 'bayesian'). Default: 'simple'.
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN, GOOGLE_ACCESS_TOKEN, GOOGLE_TOKEN_URI, GOOGLE_SCOPES: credenciales para Gmail API (si USE_EMAIL_NOTIFICATIONS=true).

## Patrones aplicados
- Ver `PATRONES_PYTHON.md` y `PATRONES_DJANGO.md` para detalles de Strategy, Factory, Signals (Observer) y Manager personalizado.
- Ver `INYECCION.md` para la explicación de inversión de dependencias en notificaciones.
- Ver `REVISION.md` para autocrítica de calidad.
- Ver `BONO_CALIFICACIONES.md` para el sistema de calificaciones (Strategy, Factory, Repository, Composite, Observer).

## Rutas principales
- `/` Inicio y reservas
- `/admin/` Administración Django
- `/adminsite/` Panel de administración de espacios
- `/rating/` Sistema de calificaciones

## Notas
- Si no se configuran credenciales de Google, el sistema no fallará: las notificaciones se envían a consola por defecto.
- Ajusta `ALLOWED_HOSTS` en `SportsConnect/settings.py` si despliegas en otro dominio/IP.
