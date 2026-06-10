
# Create your models here.
from django.db import models
from django.contrib.auth.models import User




class Departamento(models.Model):
    # pk
    DepartamentoID = models.AutoField(primary_key=True, verbose_name="ID Departamento")
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Departamento")

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        db_table = 'Departamentos'

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    MunicipioID = models.AutoField(primary_key=True, verbose_name="ID Municipio")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Municipio")
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.PROTECT, 
        related_name="municipios", 
        verbose_name="Departamento al que pertenece",
        db_column='DepartamentoID' 
    )

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
        db_table = 'Municipios'
        unique_together = ('nombre', 'departamento')

    def __str__(self):
        return f"{self.nombre} ({self.departamento.nombre})"


class Zona(models.Model):
    ZonaID = models.AutoField(primary_key=True, verbose_name="ID Zona")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Zona/Sector")
    
    # Relación 
    municipio = models.ForeignKey(
        Municipio, 
        on_delete=models.PROTECT, 
        related_name="zonas", 
        verbose_name="Municipio Asignado",
        db_column='MunicipioID'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción o Referencia")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"
        db_table = 'Zonas'
        unique_together = ('nombre', 'municipio')

    def __str__(self):
        return f"{self.nombre} - {self.municipio.nombre}"


class Red(models.Model):
    RedID = models.AutoField(primary_key=True, verbose_name="ID Red")
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Red")

    zona = models.ForeignKey(
        Zona, 
        on_delete=models.PROTECT, 
        related_name="redes", 
        verbose_name="Zona Territorial",
        db_column='ZonaID'
    )
    capacidad_maxima = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Capacidad en kW", 
        verbose_name="Capacidad Máxima"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Red Eléctrica"
        verbose_name_plural = "Redes Eléctricas"
        db_table = 'Redes'

    def __str__(self):
        return f"{self.nombre} (Zona: {self.zona.nombre})"

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
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Técnico Responsable")
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