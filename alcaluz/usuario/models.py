
# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Administrador(User):
    codigo_empleado = models.CharField(max_length=20, unique=True, verbose_name="Código empleado")
    
    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"
        #en la db tiene que aparecer en plural la tabla adminstradores
        db_table='Administradores'

    def __str__(self):
        return f"Admin: {self.username}"


class Tecnico(User):
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono de Contacto")

    class Meta:
        verbose_name = "Técnico Municipal"
        verbose_name_plural = "Técnicos Municipales"
        db_table='Tecnicos'

    def __str__(self):
        return f"Técnico: {self.username}"


class Zona(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Zona")
    

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"
        db_table='ZonasMunicipales'

    def __str__(self):
        return self.nombre


class Red(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la red")
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT, related_name="redes", verbose_name="Zona Asignada")
    class Meta:
        verbose_name = "Red Eléctrica"
        verbose_name_plural = "Redes Eléctricas"
        db_table='RedesLuminarias'

    def __str__(self):
        return f"{self.nombre} - ({self.zona.nombre})"


class Luminaria(models.Model):
    codigo_unico = models.CharField(max_length=50, unique=True, verbose_name="Código luminaria")
    red = models.ForeignKey(Red, on_delete=models.PROTECT, related_name="luminarias", verbose_name="Red Conectada")
    estado = models.BooleanField(default=True, verbose_name="Estado de Operación")

    class Meta:
        verbose_name = "Luminaria"
        verbose_name_plural = "Luminarias"
        db_table='Luminarias'

    def __str__(self):
        return f"Lumi {self.codigo_unico} ({self.red.nombre})"


class RegistroConsumo(models.Model):
    luminaria = models.ForeignKey(Luminaria, on_delete=models.CASCADE, related_name="consumos", verbose_name="Luminaria")
    registrado_por = models.ForeignKey(Tecnico, on_delete=models.SET_NULL, null=True, verbose_name="Técnico Responsable")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "registro de Consumo"
        verbose_name_plural = "Registros de Consumo"
        db_table='RegistrosConsumo'

    def save(self, *args, **kwargs):
        tarifa_kwh = 0.15 
        self.costo_calculado = float(self.consumo_kwh) * tarifa_kwh
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Consumo es xd"