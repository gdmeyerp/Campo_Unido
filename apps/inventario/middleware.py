from django.http import HttpResponseForbidden
from django.urls import resolve
from django.shortcuts import redirect
from django.contrib import messages

from .models import ProductoInventario

class ProductoAccesoMiddleware:
    """
    Middleware para verificar que los usuarios solo accedan a sus propios productos
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Procesar request antes de la vista
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        path = request.path
        
        # Solo procesar vistas de detalle, edición y eliminación de productos
        if path.startswith('/inventario/producto/'):
            try:
                # Obtener el ID del producto de la URL
                url_parts = path.split('/')
                product_id = None
                
                for i, part in enumerate(url_parts):
                    if part == 'producto' and i+1 < len(url_parts) and url_parts[i+1].isdigit():
                        product_id = int(url_parts[i+1])
                        break
                
                if product_id:
                    # Verificar si el producto pertenece al usuario
                    try:
                        producto = ProductoInventario.objects.get(id=product_id)
                        if producto.propietario and producto.propietario != request.user:
                            messages.error(request, "No tienes permisos para acceder a este producto.")
                            return redirect('inventario:lista_productos')
                    except ProductoInventario.DoesNotExist:
                        pass  # Dejar que la vista maneje el 404
            except Exception as e:
                # Si hay algún error, dejar pasar la solicitud y que la vista lo maneje
                pass
                
        # Continuar con el flujo normal
        response = self.get_response(request)
        return response 