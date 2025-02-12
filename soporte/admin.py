from django.contrib import admin
from .models import (
    CategoriaTicket, PrioridadTicket, EstadoTicket, TicketSoporte, 
    HistorialTicket, SLA, SLATicket, EscalamientoTicket, EtiquetaProblema, TicketEtiqueta
)

admin.site.register(CategoriaTicket)
admin.site.register(PrioridadTicket)
admin.site.register(EstadoTicket)
admin.site.register(TicketSoporte)
admin.site.register(HistorialTicket)
admin.site.register(SLA)
admin.site.register(SLATicket)
admin.site.register(EscalamientoTicket)
admin.site.register(EtiquetaProblema)
admin.site.register(TicketEtiqueta)
