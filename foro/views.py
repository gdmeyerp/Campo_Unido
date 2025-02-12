from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Foro, PublicacionForo, ComentarioPublicacion
from .forms import ForoForm, PublicacionForm, ComentarioForm
from django.shortcuts import render, get_object_or_404
from .models import CategoriaForo, Foro


def foro_general(request):
    categorias = CategoriaForo.objects.all()
    context = {
        'categorias': categorias,
    }
    return render(request, 'foro/foro_general.html', context)

# Vista para listar todos los foros
class ListaForosView(ListView):
    model = Foro
    template_name = 'foro/lista_foros.html'
    context_object_name = 'foros'

# Vista para ver los detalles de un foro específico
class DetalleForoView(DetailView):
    model = Foro
    template_name = 'foro/detalle_foro.html'
    context_object_name = 'foro'

# Vista para crear un nuevo foro
class CrearForoView(CreateView):
    model = Foro
    form_class = ForoForm
    template_name = 'foro/crear_foro.html'
    success_url = reverse_lazy('foro:lista_foros')

# Vista para editar un foro existente
class EditarForoView(UpdateView):
    model = Foro
    form_class = ForoForm
    template_name = 'foro/editar_foro.html'
    success_url = reverse_lazy('foro:lista_foros')

# Vista para eliminar un foro
class EliminarForoView(DeleteView):
    model = Foro
    template_name = 'foro/eliminar_foro.html'
    success_url = reverse_lazy('foro:lista_foros')

# Vista para crear una nueva publicación en un foro
class CrearPublicacionView(CreateView):
    model = PublicacionForo
    form_class = PublicacionForm
    template_name = 'foro/crear_publicacion.html'

    def form_valid(self, form):
        form.instance.foro_id = self.kwargs['foro_id']
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('foro:lista_foros')

# Vista para ver los detalles de una publicación específica
class DetallePublicacionView(DetailView):
    model = PublicacionForo
    template_name = 'foro/detalle_publicacion.html'
    context_object_name = 'publicacion'

# Vista para editar una publicación existente
class EditarPublicacionView(UpdateView):
    model = PublicacionForo
    form_class = PublicacionForm
    template_name = 'foro/editar_publicacion.html'
    success_url = reverse_lazy('foro:lista_foros')

# Vista para eliminar una publicación
class EliminarPublicacionView(DeleteView):
    model = PublicacionForo
    template_name = 'foro/eliminar_publicacion.html'
    success_url = reverse_lazy('foro:lista_foros')

# Vista para crear un nuevo comentario en una publicación
class CrearComentarioView(CreateView):
    model = ComentarioPublicacion
    form_class = ComentarioForm
    template_name = 'foro/crear_comentario.html'

    def form_valid(self, form):
        form.instance.publicacion_id = self.kwargs['publicacion_id']
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('foro:lista_foros')

# Vista para editar un comentario existente
class EditarComentarioView(UpdateView):
    model = ComentarioPublicacion
    form_class = ComentarioForm
    template_name = 'foro/editar_comentario.html'
    success_url = reverse_lazy('foro:lista_foros')

# Vista para eliminar un comentario
class EliminarComentarioView(DeleteView):
    model = ComentarioPublicacion
    template_name = 'foro/eliminar_comentario.html'
    success_url = reverse_lazy('foro:lista_foros')
