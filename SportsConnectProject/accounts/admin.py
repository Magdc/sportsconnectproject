from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import CustomUserCreationForm

class UserAdmin(BaseUserAdmin):
    form = CustomUserCreationForm
    model = User
    list_display = ['email', 'first_name', 'last_name', 'last_name2', 'phone', 'is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'last_name2', 'phone')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_student', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'last_name2', 'phone', 'password1', 'password2', 'is_student', 'is_staff', 'is_superuser')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name', 'last_name2')
    ordering = ('email',)

admin.site.register(User, UserAdmin)