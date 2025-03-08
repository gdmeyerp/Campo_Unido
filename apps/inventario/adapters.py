from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import ProductoInventario, MovimientoInventario

class InventarioAdapter:
    """
    Adaptador para el módulo de inventario.
    Proporciona una interfaz unificada que será utilizada por el marketplace.
    """
    
    def get_product_info(self, product_id):
        """
        Obtiene información completa de un producto de inventario.
        """
        try:
            producto = ProductoInventario.objects.get(id=product_id)
            
            return {
                "success": True,
                "data": {
                    "id": producto.id,
                    "nombre": producto.nombre_producto,
                    "descripcion": producto.descripcion_producto or "",
                    "precio_venta": float(producto.precio_venta),
                    "precio_compra": float(producto.precio_compra),
                    "cantidad_disponible": producto.cantidad_disponible,
                    "stock_minimo": getattr(producto, 'stock_minimo', 1)
                }
            }
        except ProductoInventario.DoesNotExist:
            return {
                "success": False,
                "message": "Producto no encontrado"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al obtener producto: {str(e)}"
            }
    
    def update_stock(self, product_id, quantity, user, operation="decrease"):
        """
        Actualiza el stock de un producto y registra el movimiento.
        operation: "decrease" (default) o "increase"
        """
        try:
            with transaction.atomic():
                producto = ProductoInventario.objects.get(id=product_id)
                
                # Verificar stock antes de proceder
                if operation == "decrease" and producto.cantidad_disponible < quantity:
                    return {
                        "success": False,
                        "message": "No hay suficiente stock disponible"
                    }
                
                # Determinar tipo de movimiento
                tipo_movimiento = "SALIDA" if operation == "decrease" else "ENTRADA"
                
                # Crear movimiento de inventario
                MovimientoInventario.objects.create(
                    producto_inventario=producto,
                    tipo_movimiento=tipo_movimiento,
                    cantidad_movimiento=quantity,
                    usuario=user,
                    descripcion_movimiento=f"Movimiento desde Marketplace - {'venta' if operation == 'decrease' else 'devolución'}",
                    referencia_documento=f"MARKETPLACE-{product_id}",
                    tipo_documento="MARKETPLACE"
                )
                
                # El stock se actualiza automáticamente mediante signals
                
                return {
                    "success": True,
                    "message": f"Stock actualizado correctamente",
                    "current_stock": producto.cantidad_disponible
                }
                
        except ProductoInventario.DoesNotExist:
            return {
                "success": False,
                "message": "Producto no encontrado"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al actualizar stock: {str(e)}"
            }
    
    def get_products_list(self, **filters):
        """
        Obtiene una lista de productos que cumplen con los filtros especificados.
        """
        try:
            # Filtro por defecto: productos con stock disponible
            queryset = ProductoInventario.objects.filter(
                cantidad_disponible__gt=0
            )
            
            # Añadir filtros adicionales
            if 'categoria' in filters:
                queryset = queryset.filter(categoria__id=filters['categoria'])
                
            if 'search' in filters:
                queryset = queryset.filter(nombre_producto__icontains=filters['search'])
                
            if 'min_price' in filters:
                queryset = queryset.filter(precio_venta__gte=filters['min_price'])
                
            if 'max_price' in filters:
                queryset = queryset.filter(precio_venta__lte=filters['max_price'])
            
            # Limitar resultados (paginación)
            limit = filters.get('limit', 50)
            queryset = queryset[:limit]
            
            # Convertir a formato de respuesta
            productos = []
            for producto in queryset:
                productos.append({
                    "id": producto.id,
                    "nombre": producto.nombre_producto,
                    "descripcion": producto.descripcion_producto or "",
                    "precio_venta": float(producto.precio_venta),
                    "cantidad_disponible": producto.cantidad_disponible
                })
            
            return {
                "success": True,
                "data": productos,
                "count": len(productos)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al obtener lista de productos: {str(e)}"
            } 