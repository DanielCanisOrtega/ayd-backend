from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.conf import settings

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
    
class StudentProfile(models.Model):
    #atributos de un estudiante
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código institucional")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    carrera = models.CharField(max_length=100, blank=True, verbose_name="Carrera")

    def __str__(self):
        return f"Perfil de {self.user.username} (Estudiante)"
    
      
# Perfil para Profesor
class TeacherProfile(models.Model):
    #atributos de un profesor
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    #definir si un profesor tiene código o no
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    department = models.CharField(max_length=100, blank=True, verbose_name="Departamento")

    def __str__(self):
        return f"Perfil de {self.user.username} (Docente)"
    
# Perfil para Administrador
class AdminProfile(models.Model):
    #atributos de un administrador --> DEFINIR
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')

    def __str__(self):
        return f"Perfil de {self.user.username} (Administrador)"
    
# Señales para crear automáticamente los perfiles
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.user_type == 'teacher':
            TeacherProfile.objects.create(user=instance)
        elif instance.user_type == 'admin':
            AdminProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 'student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.user_type == 'teacher' and hasattr(instance, 'teacher_profile'):
        instance.teacher_profile.save()
    elif instance.user_type == 'admin' and hasattr(instance, 'admin_profile'):
        instance.admin_profile.save()
        
# Modelo Proyecto
class Proyecto(models.Model):
    ESTADO_CHOICES = [
        ('not_started', 'Sin Iniciar'),
        ('in_progress', 'En Ejecución'),
        ('finished', 'Terminado'),
    ]
    
    titulo = models.CharField(max_length=255, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción")
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default='not_started', verbose_name="Estado"
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")

    def __str__(self):
        return self.titulo


# Modelo Actividad
class Actividad(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='actividades')
    titulo = models.CharField(max_length=255, verbose_name="Título de Actividad")
    descripcion = models.TextField(verbose_name="Descripción de Actividad")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")

    def __str__(self):
        return self.titulo
    
# Modelo Recurso (relacionado con Actividad)
class Recurso(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='recursos')
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Recurso")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Recurso")
    archivo = models.FileField(upload_to='recursos/', blank=True, verbose_name="Archivo del Recurso")

    def __str__(self):
        return f"Recurso {self.nombre} para {self.actividad.titulo}"


# Modelo Cronograma
class Cronograma(models.Model):
    proyecto = models.OneToOneField(Proyecto, on_delete=models.CASCADE, related_name='cronograma')
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name="Fecha de Creación")

    def __str__(self):
        return f"Cronograma de {self.proyecto.titulo}"
    
# Modelo Hito (relacionado con Cronograma)
class Hito(models.Model):
    cronograma = models.ForeignKey(Cronograma, on_delete=models.CASCADE, related_name='hitos')
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Hito")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Hito")
    fecha_cumplimiento = models.DateField(verbose_name="Fecha de Cumplimiento")

    def __str__(self):
        return f"Hito {self.nombre} para {self.cronograma.proyecto.titulo}"


# Modelo Participante
class Participante(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='participantes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rol = models.CharField(max_length=100, verbose_name="Rol en el Proyecto")

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"


# Modelo Documento
class Documento(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='documentos')
    archivo = models.FileField(upload_to='documentos/', verbose_name="Archivo")
    fecha_subida = models.DateField(auto_now_add=True, verbose_name="Fecha de Subida")

    def __str__(self):
        return f"Documento {self.id} del Proyecto {self.proyecto.titulo}"


# Modelo Reporte
class Reporte(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='reportes')
    estado = models.CharField(max_length=20, choices=Proyecto.ESTADO_CHOICES, verbose_name="Estado del Proyecto")
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name="Fecha de Creación")
    archivo = models.FileField(upload_to='reportes/', verbose_name="Archivo del Reporte")

    def __str__(self):
        return f"Reporte de {self.proyecto.titulo} - {self.estado}"