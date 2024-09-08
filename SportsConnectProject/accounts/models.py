from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    idUser = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)  
    last_name2 = models.CharField(max_length=150, blank=True, null =True, verbose_name="Second last name")
    phone = models.IntegerField(blank=True, null=True, verbose_name="Cellphone")
    is_student = models.BooleanField(default=False, verbose_name="is student")

    objects = CustomUserManager()
    username = None  # Eliminar el campo username

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['first_name', 'last_name']
    

    def __str__(self):
        return f"({self.email}) {self.first_name} {self.last_name} {self.last_name2} "

# Create your models here.
