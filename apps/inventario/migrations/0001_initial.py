# Generated by Django 5.1.6 on 2025-03-04 21:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Almacen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_almacen', models.CharField(max_length=255)),
                ('direccion', models.CharField(max_length=255)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_estado', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PedidoProveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_pedido', models.DateField()),
                ('fecha_entrega', models.DateField(blank=True, null=True)),
                ('estado_pedido', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_proveedor', models.CharField(max_length=255)),
                ('rif', models.CharField(blank=True, max_length=20, null=True, verbose_name='RIF')),
                ('direccion', models.CharField(max_length=255)),
                ('telefono', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('contacto', models.CharField(blank=True, max_length=100, null=True, verbose_name='Persona de contacto')),
                ('categoria', models.CharField(blank=True, max_length=50, null=True, verbose_name='Categoría')),
                ('notas', models.TextField(blank=True, null=True, verbose_name='Notas adicionales')),
            ],
        ),
        migrations.CreateModel(
            name='UnidadMedida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_unidad', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CategoriaProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_categoria', models.CharField(max_length=255)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('categoria_padre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcategorias', to='inventario.categoriaproducto')),
            ],
        ),
        migrations.CreateModel(
            name='ProductoInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_producto', models.CharField(max_length=255)),
                ('descripcion_producto', models.TextField(blank=True, null=True)),
                ('cantidad_disponible', models.IntegerField()),
                ('stock_minimo', models.IntegerField()),
                ('precio_compra', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_venta', models.DecimalField(decimal_places=2, max_digits=10)),
                ('categoria_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.categoriaproducto')),
                ('estado_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.estadoproducto')),
            ],
        ),
        migrations.CreateModel(
            name='MovimientoInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_movimiento', models.CharField(max_length=50)),
                ('cantidad_movimiento', models.IntegerField()),
                ('fecha_movimiento', models.DateTimeField(auto_now_add=True)),
                ('descripcion_movimiento', models.TextField(blank=True, null=True)),
                ('referencia_documento', models.CharField(blank=True, max_length=255, null=True)),
                ('tipo_documento', models.CharField(blank=True, max_length=50, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('producto_inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.productoinventario')),
            ],
        ),
        migrations.CreateModel(
            name='DetallePedidoProveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pedido_proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.pedidoproveedor')),
                ('producto_inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.productoinventario')),
            ],
        ),
        migrations.CreateModel(
            name='CaducidadProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_caducidad', models.DateField()),
                ('cantidad_disponible', models.IntegerField()),
                ('producto_inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.productoinventario')),
            ],
        ),
        migrations.CreateModel(
            name='AlertaStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_alerta', models.DateTimeField(auto_now_add=True)),
                ('cantidad_disponible', models.IntegerField()),
                ('producto_inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.productoinventario')),
            ],
        ),
        migrations.AddField(
            model_name='pedidoproveedor',
            name='proveedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.proveedor'),
        ),
        migrations.CreateModel(
            name='ReservaInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_reservada', models.IntegerField()),
                ('carrito_id', models.IntegerField()),
                ('fecha_reserva', models.DateTimeField(auto_now_add=True)),
                ('fecha_expiracion', models.DateTimeField()),
                ('producto_inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.productoinventario')),
            ],
        ),
        migrations.CreateModel(
            name='UbicacionAlmacen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_ubicacion', models.CharField(max_length=255)),
                ('almacen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.almacen')),
            ],
        ),
        migrations.CreateModel(
            name='InventarioAlmacen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_disponible', models.IntegerField()),
                ('producto_inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.productoinventario')),
                ('ubicacion_almacen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.ubicacionalmacen')),
            ],
        ),
    ]
