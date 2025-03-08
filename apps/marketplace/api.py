from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.text import slugify
from .models import MarketplaceProducto, CategoriaProducto, ImagenProducto

class ProductSourceAdapter:
    """
    Clase base para adaptadores que traen productos de fuentes externas.
    Este patrón adaptador permite que marketplace no dependa directamente
    de los modelos de otros módulos.
    """
    def get_product_info(self, product_id):
        """
        Obtiene información del producto desde la fuente externa.
        Debe ser implementado por las clases hijas.
        """
        raise NotImplementedError("Subclasses must implement get_product_info")

    def update_stock(self, product_id, quantity, user, operation="decrease"):
        """
        Actualiza el stock en la fuente externa.
        Debe ser implementado por las clases hijas.
        """
        raise NotImplementedError("Subclasses must implement update_stock")
    
    def get_products_list(self, **filters):
        """
        Obtiene una lista de productos desde la fuente externa.
        Debe ser implementado por las clases hijas.
        """
        raise NotImplementedError("Subclasses must implement get_products_list")


def get_adapter_for_source(source_name):
    """
    Factory que retorna el adaptador adecuado para una fuente específica.
    """
    # Importaciones dinámicas para evitar dependencias circulares
    if source_name == "inventario":
        from apps.inventario.adapters import InventarioAdapter
        return InventarioAdapter()
    # Se pueden añadir más adaptadores según se necesite
    return None


def create_marketplace_product(form_data, user, source="inventario"):
    """
    Crea un producto en el marketplace a partir de datos de un formulario
    y una fuente externa, usando el adaptador apropiado.
    """
    try:
        # Obtener el adaptador adecuado
        adapter = get_adapter_for_source(source)
        if not adapter:
            return {
                "success": False,
                "message": f"No se encontró un adaptador para la fuente: {source}"
            }
        
        # Extraer data del formulario
        producto_id = form_data.get("id_producto_externo")
        cantidad = form_data.get("cantidad_a_vender")
        
        # Obtener información del producto usando el adaptador
        producto_info = adapter.get_product_info(producto_id)
        if not producto_info["success"]:
            return producto_info
        
        # Verificar stock antes de proceder
        if producto_info["data"]["cantidad_disponible"] < cantidad:
            return {
                "success": False,
                "message": "No hay suficiente stock disponible"
            }
            
        with transaction.atomic():
            # Crear producto en marketplace
            producto_marketplace = MarketplaceProducto(
                vendedor_id_id=user,
                nombre_producto=form_data.get("nombre_producto"),
                descripcion=form_data.get("descripcion"),
                categoria_producto_id_id=form_data.get("categoria_producto_id_id"),
                estado_producto_id_id=form_data.get("estado_producto_id_id"),
                unidad_medida_id_id=form_data.get("unidad_medida_id_id"),
                precio_base=form_data.get("precio_base"),
                precio_actual=form_data.get("precio_base"),
                stock_actual=cantidad,
                stock_minimo=producto_info["data"].get("stock_minimo", cantidad // 2),
                imagen_principal=form_data.get("imagen_principal"),
                disponibilidad=True,
                destacado=form_data.get("destacado", False),
                es_organico=form_data.get("es_organico", False),
                slug=slugify(form_data.get("nombre_producto")),
                # Campos adicionales para la interfaz
                producto_externo_id=producto_id,
                sistema_origen=source
            )
            producto_marketplace.save()
            
            # Guardar imágenes adicionales
            for field_name in ['imagen_adicional1', 'imagen_adicional2', 'imagen_adicional3']:
                imagen = form_data.get(field_name)
                if imagen:
                    ImagenProducto.objects.create(
                        producto=producto_marketplace,
                        imagen=imagen
                    )
            
            # Actualizar stock en la fuente original a través del adaptador
            adapter.update_stock(
                product_id=producto_id,
                quantity=cantidad,
                user=user
            )
            
            return {
                "success": True,
                "message": "Producto agregado exitosamente al marketplace",
                "product_id": producto_marketplace.producto_id
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al crear producto: {str(e)}"
        }


def get_external_product(product_id, source="inventario"):
    """
    Obtiene información de un producto desde una fuente externa.
    """
    adapter = get_adapter_for_source(source)
    if not adapter:
        return {
            "success": False,
            "message": f"No se encontró un adaptador para la fuente: {source}"
        }
    
    return adapter.get_product_info(product_id)


def get_external_products_list(source="inventario", **filters):
    """
    Obtiene una lista de productos desde una fuente externa.
    """
    adapter = get_adapter_for_source(source)
    if not adapter:
        return {
            "success": False,
            "message": f"No se encontró un adaptador para la fuente: {source}"
        }
    
    return adapter.get_products_list(**filters) 