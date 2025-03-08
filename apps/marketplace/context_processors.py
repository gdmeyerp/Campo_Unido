from .models import CarritoCompra, Product
from django.db import DatabaseError

def cart_processor(request):
    """
    Context processor to make cart information available to all templates.
    """
    cart_count = 0
    
    if request.user.is_authenticated:
        try:
            cart_items = CarritoCompra.objects.filter(usuario=request.user, activo=True)
            cart_count = sum(item.cantidad for item in cart_items)
        except (DatabaseError, Exception) as e:
            pass
    
    return {
        'cart_count': cart_count
    }

def marketplace_context(request):
    """
    Proporciona los productos destacados para el marketplace preview.
    """
    marketplace_products = Product.objects.filter(is_active=True).order_by('-created_at')[:6]
    return {
        'marketplace_products': marketplace_products
    } 