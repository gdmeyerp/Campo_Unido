# Generated by Django 5.1.6 on 2025-04-29 18:49

import django.core.validators
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
            name='TarifaEnvio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distancia_min', models.DecimalField(decimal_places=2, help_text='Distancia mínima en kilómetros', max_digits=5)),
                ('distancia_max', models.DecimalField(decimal_places=2, help_text='Distancia máxima en kilómetros', max_digits=5)),
                ('costo', models.DecimalField(decimal_places=2, help_text='Costo del envío', max_digits=10)),
            ],
            options={
                'verbose_name': 'Tarifa de Envío',
                'verbose_name_plural': 'Tarifas de Envío',
                'ordering': ['distancia_min'],
            },
        ),
        migrations.CreateModel(
            name='CategoriaProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='categorias/')),
                ('activa', models.BooleanField(default=True)),
                ('categoria_padre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcategorias', to='marketplaceV1.categoriaproducto')),
            ],
            options={
                'verbose_name': 'Categoría de Producto',
                'verbose_name_plural': 'Categorías de Productos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_compra', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado'), ('enviado', 'Enviado'), ('entregado', 'Entregado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=20)),
                ('direccion_envio', models.TextField(blank=True, null=True)),
                ('metodo_pago', models.CharField(blank=True, max_length=100, null=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compras_v1', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Compra',
                'verbose_name_plural': 'Compras',
                'ordering': ['-fecha_compra'],
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='productos/')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('destacado', models.BooleanField(default=False)),
                ('estado', models.CharField(default='disponible', max_length=50)),
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productos', to='marketplaceV1.categoriaproducto')),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos_v1', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='DetalleCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='marketplaceV1.compra')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplaceV1.producto')),
            ],
            options={
                'verbose_name': 'Detalle de Compra',
                'verbose_name_plural': 'Detalles de Compra',
            },
        ),
        migrations.AddField(
            model_name='compra',
            name='productos',
            field=models.ManyToManyField(through='marketplaceV1.DetalleCompra', to='marketplaceV1.producto'),
        ),
        migrations.CreateModel(
            name='ProductoImagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='productos/imagenes/')),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='marketplaceV1.producto')),
            ],
            options={
                'verbose_name': 'Imagen de Producto',
                'verbose_name_plural': 'Imágenes de Productos',
                'ordering': ['orden', 'fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='ValoracionProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calificacion', models.PositiveSmallIntegerField(default=5, validators=[django.core.validators.MinValueValidator(1)])),
                ('titulo', models.CharField(max_length=100)),
                ('comentario', models.TextField()),
                ('fecha_valoracion', models.DateTimeField(auto_now_add=True)),
                ('utilidad', models.PositiveIntegerField(default=0)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplaceV1.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='valoraciones_v1', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Valoración de Producto',
                'verbose_name_plural': 'Valoraciones de Productos',
                'ordering': ['-fecha_valoracion'],
                'unique_together': {('producto', 'usuario')},
            },
        ),
        migrations.CreateModel(
            name='RespuestaValoracion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respuesta', models.TextField()),
                ('fecha_respuesta', models.DateTimeField(auto_now_add=True)),
                ('valoracion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respuestas', to='marketplaceV1.valoracionproducto')),
            ],
            options={
                'verbose_name': 'Respuesta a Valoración',
                'verbose_name_plural': 'Respuestas a Valoraciones',
            },
        ),
        migrations.CreateModel(
            name='ListaDeseos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_agregado', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lista_deseos_v1', to=settings.AUTH_USER_MODEL)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplaceV1.producto')),
            ],
            options={
                'verbose_name': 'Lista de Deseos',
                'verbose_name_plural': 'Listas de Deseos',
                'db_table': 'marketplaceV1_lista_deseos',
                'unique_together': {('usuario', 'producto')},
            },
        ),
        migrations.CreateModel(
            name='CarritoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('fecha_agregado', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrito_items_v1', to=settings.AUTH_USER_MODEL)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplaceV1.producto')),
            ],
            options={
                'verbose_name': 'Item de Carrito',
                'verbose_name_plural': 'Items de Carrito',
                'unique_together': {('usuario', 'producto')},
            },
        ),
    ]
