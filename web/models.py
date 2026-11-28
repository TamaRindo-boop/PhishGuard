from django.db import models
from django.contrib.auth.models import User

class EvaluacionRiesgo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    severidad = models.IntegerField()
    probabilidad = models.IntegerField()
    exposicion = models.IntegerField()
    controles = models.IntegerField()
    puntuacion = models.FloatField()
    nivel = models.CharField(max_length=20)
    recomendacion = models.TextField()

    def __str__(self):
        return f"{self.usuario.username} - {self.nivel} ({self.puntuacion})"

# --- NUEVA TABLA PARA EL HISTORIAL DE URLs ---
class AnalisisURL(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=500)
    nivel = models.CharField(max_length=20)
    puntuacion = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.url} - {self.nivel}"