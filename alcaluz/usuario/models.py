
# Create your models here.
from django.db import models
from django.contrib.auth.models import User




class Departamento(models.Model):
    id_departamento = models.AutoField(primary_key=True)
    nom_departamento = models.CharField(max_length=255)

    class Meta:
        db_table = 'Departamento'

    def __str__(self):
        return self.nom_departamento


class Municipio(models.Model):
    id_municipio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        db_column='id_departamento'
    )

    class Meta:
        db_table = 'Municipio'

    def __str__(self):
        return self.nombre


class Zona(models.Model):
    id_zona = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    tipo_zona = models.CharField(max_length=255, blank=True, null=True)

    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.PROTECT,
        db_column='id_municipio'
    )

    class Meta:
        db_table = 'Zona'

    def __str__(self):
        return self.nombre


class Red(models.Model):
    id_red = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    zona = models.ForeignKey(
        Zona,
        on_delete=models.PROTECT,
        db_column='id_zona'
    )

    class Meta:
        db_table = 'Red'

    def __str__(self):
        return self.nombre

class Luminaria(models.Model):
    id_luminaria = models.AutoField(primary_key=True)
    potencia = models.CharField(max_length=255, blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    fecha_instalacion = models.DateField(blank=True, null=True)

    red = models.ForeignKey(
        Red,
        on_delete=models.PROTECT,
        db_column='id_red'
    )

    class Meta:
        db_table = 'Luminaria'

    def __str__(self):
        return f"Luminaria {self.id_luminaria}"


class RegistroConsumo(models.Model):
    id_registro = models.AutoField(primary_key=True)

    consumo_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    periodo_inicio = models.DateField()
    fecha_registro = models.DateField(auto_now_add=True)
    periodo_fin = models.DateField()

    luminaria = models.ForeignKey(
        Luminaria,
        on_delete=models.PROTECT,
        db_column='id_luminaria'
    )

    tecnico = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='id_tecnico'
    )

    class Meta:
        db_table = 'RegistroConsumo'

    def __str__(self):
        return f"Registro {self.id_registro}"
    

class Reporte(models.Model):
    id_reporte = models.AutoField(primary_key=True, verbose_name="ID Reporte")
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Generación")
    tipo_nivel = models.CharField(max_length=100, verbose_name="Tipo de Nivel")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    total_kwh = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total kWh")
    total_costo = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total Costo")

    # Relación con el usuario administrador
    admin = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reportes_generados",
        verbose_name="Administrador Responsable"
    )

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        db_table = 'Reporte'

    def __str__(self):
        return f"Reporte {self.id_reporte} - {self.fecha_generacion.date()}"
