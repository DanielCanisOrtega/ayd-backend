from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('student', 'Estudiante'),
        ('teacher', 'Docente'),
        ('admin', 'Administrador'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
        verbose_name="Tipo de Usuario"
    )

    def is_student(self):
        return self.user_type == 'student'

    def is_teacher(self):
        return self.user_type == 'teacher'

    def is_admin(self):
        return self.user_type == 'admin'

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
class Student(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='Estudiante')
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código institucional")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    carrera = models.CharField(max_length=100, blank=True, verbose_name="Carrera")

    def __str__(self):
        return f"Perfil de {self.user.username} (Estudiante)"    
