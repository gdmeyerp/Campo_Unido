from django.db import models
from core.models import User

# Categoría de los tickets de soporte técnico
class CategoriaTicket(models.Model):
    categoria_ticket_id = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100)
    descripcion_categoria = models.TextField()

    def __str__(self):
        return self.nombre_categoria

# Prioridad de los tickets
class PrioridadTicket(models.Model):
    prioridad_ticket_id = models.AutoField(primary_key=True)
    nombre_prioridad = models.CharField(max_length=50)  # Ejemplos: "Alta", "Media", "Baja"
    tiempo_respuesta_estimado = models.DurationField()  # Tiempo promedio de respuesta según prioridad

    def __str__(self):
        return self.nombre_prioridad

# Estado de los tickets de soporte
class EstadoTicket(models.Model):
    estado_ticket_id = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=50)  # Ejemplos: "Abierto", "En Progreso", "Resuelto", "Escalado", "Cerrado"
    descripcion_estado = models.TextField()

    def __str__(self):
        return self.nombre_estado

# Modelo principal para la gestión de tickets de soporte
class TicketSoporte(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    usuario_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_creados')  # Usuario que creó el ticket
    tecnico_asignado_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_asignados')  # Técnico asignado para resolver el ticket
    categoria_ticket_id = models.ForeignKey(CategoriaTicket, on_delete=models.CASCADE)
    prioridad_ticket_id = models.ForeignKey(PrioridadTicket, on_delete=models.CASCADE)
    estado_ticket_id = models.ForeignKey(EstadoTicket, on_delete=models.CASCADE)
    descripcion_problema = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Ticket #{self.ticket_id} - {self.descripcion_problema[:30]}'

# Historial de acciones sobre los tickets
class HistorialTicket(models.Model):
    historial_ticket_id = models.AutoField(primary_key=True)
    ticket_id = models.ForeignKey(TicketSoporte, on_delete=models.CASCADE)
    usuario_responsable_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    estado_ticket_id = models.ForeignKey(EstadoTicket, on_delete=models.CASCADE)
    accion_realizada = models.TextField()  # Ejemplos: "Ticket actualizado", "Ticket escalado"
    fecha_accion = models.DateTimeField(auto_now_add=True)

# Modelo para la gestión de SLA (Service Level Agreement)
class SLA(models.Model):
    sla_id = models.AutoField(primary_key=True)
    nombre_sla = models.CharField(max_length=100)  # Ejemplos: "Respuesta Rápida", "Resolución Completa"
    descripcion_sla = models.TextField()
    tiempo_resolucion_maximo = models.DurationField()  # Tiempo máximo para resolver el ticket según el SLA

    def __str__(self):
        return self.nombre_sla

# Relación entre los tickets y el SLA
class SLATicket(models.Model):
    sla_ticket_id = models.AutoField(primary_key=True)
    ticket_id = models.ForeignKey(TicketSoporte, on_delete=models.CASCADE)
    sla_id = models.ForeignKey(SLA, on_delete=models.CASCADE)
    fecha_inicio_sla = models.DateTimeField(auto_now_add=True)
    fecha_fin_sla = models.DateTimeField(null=True, blank=True)
    estado_sla = models.CharField(max_length=50)  # Ejemplos: "Cumplido", "No cumplido", "En Proceso"

# Modelo para la escalación de tickets
class EscalamientoTicket(models.Model):
    escalamiento_id = models.AutoField(primary_key=True)
    ticket_id = models.ForeignKey(TicketSoporte, on_delete=models.CASCADE)
    nivel_escalamiento = models.IntegerField()  # Nivel de escalamiento del problema
    motivo_escalamiento = models.TextField()
    fecha_escalamiento = models.DateTimeField(auto_now_add=True)
    tecnico_escalado_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tickets_escalados')

# Etiquetas para clasificar problemas en los tickets
class EtiquetaProblema(models.Model):
    etiqueta_problema_id = models.AutoField(primary_key=True)
    nombre_etiqueta = models.CharField(max_length=100)  # Ejemplos: "Conectividad", "Hardware", "Software", "Urgente"

    def __str__(self):
        return self.nombre_etiqueta

# Relación entre los tickets y sus etiquetas
class TicketEtiqueta(models.Model):
    ticket_etiqueta_id = models.AutoField(primary_key=True)
    ticket_id = models.ForeignKey(TicketSoporte, on_delete=models.CASCADE)
    etiqueta_problema_id = models.ForeignKey(EtiquetaProblema, on_delete=models.CASCADE)
