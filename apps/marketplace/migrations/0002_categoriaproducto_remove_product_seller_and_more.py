# Generated by Django 5.1.6 on 2025-03-12 23:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='categorias/')),
                ('activa', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Categoría de Producto',
                'verbose_name_plural': 'Categorías de Productos',
                'ordering': ['nombre'],
            },
        ),
        migrations.RemoveField(
            model_name='product',
            name='seller',
        ),
        migrations.RemoveField(
            model_name='compra',
            name='producto',
        ),
        migrations.AlterModelOptions(
            name='compra',
            options={'ordering': ['-fecha_compra'], 'verbose_name': 'Compra', 'verbose_name_plural': 'Compras'},
        ),
        migrations.AlterModelOptions(
            name='listadeseos',
            options={'verbose_name': 'Lista de Deseos', 'verbose_name_plural': 'Listas de Deseos'},
        ),
        migrations.RenameField(
            model_name='compra',
            old_name='precio_total',
            new_name='total',
        ),
        migrations.RenameField(
            model_name='listadeseos',
            old_name='fecha_creacion',
            new_name='fecha_agregado',
        ),
        migrations.RemoveField(
            model_name='compra',
            name='cantidad',
        ),
        migrations.RemoveField(
            model_name='compra',
            name='comprador',
        ),
        migrations.AddField(
            model_name='compra',
            name='direccion_envio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='compra',
            name='metodo_pago',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='compra',
            name='usuario',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='compras', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compra',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado'), ('enviado', 'Enviado'), ('entregado', 'Entregado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=20),
        ),
        migrations.AlterField(
            model_name='listadeseos',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lista_deseos', to=settings.AUTH_USER_MODEL),
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
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productos', to='marketplace.categoriaproducto')),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to=settings.AUTH_USER_MODEL)),
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
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='marketplace.compra')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.producto')),
            ],
            options={
                'verbose_name': 'Detalle de Compra',
                'verbose_name_plural': 'Detalles de Compra',
            },
        ),
        migrations.CreateModel(
            name='CarritoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('fecha_agregado', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carrito_items', to=settings.AUTH_USER_MODEL)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.producto')),
            ],
            options={
                'verbose_name': 'Item de Carrito',
                'verbose_name_plural': 'Items de Carrito',
                'unique_together': {('usuario', 'producto')},
            },
        ),
        migrations.AddField(
            model_name='compra',
            name='productos',
            field=models.ManyToManyField(through='marketplace.DetalleCompra', to='marketplace.producto'),
        ),
        migrations.AlterField(
            model_name='listadeseos',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.producto'),
        ),
        migrations.AlterUniqueTogether(
            name='listadeseos',
            unique_together={('usuario', 'producto')},
        ),
        migrations.DeleteModel(
            name='CarritoCompra',
        ),
        migrations.DeleteModel(
            name='Product',
        ),
    ]
