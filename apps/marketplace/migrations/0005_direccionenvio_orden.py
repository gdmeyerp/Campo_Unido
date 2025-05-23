# Generated by Django 5.1.6 on 2025-04-30 21:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_add_more_categories'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DireccionEnvio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_completo', models.CharField(max_length=200)),
                ('telefono', models.CharField(max_length=20)),
                ('direccion', models.CharField(max_length=255)),
                ('ciudad', models.CharField(max_length=100)),
                ('departamento', models.CharField(max_length=100)),
                ('codigo_postal', models.CharField(blank=True, max_length=10, null=True)),
                ('notas_adicionales', models.TextField(blank=True, null=True)),
                ('predeterminada', models.BooleanField(default=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='direcciones_envio_marketplace', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Dirección de Envío',
                'verbose_name_plural': 'Direcciones de Envío',
            },
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_orden', models.CharField(help_text='Número único de la orden', max_length=20, unique=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('estado', models.CharField(choices=[('creada', 'Creada'), ('pendiente_pago', 'Pendiente de pago'), ('pagada', 'Pagada'), ('preparando', 'Preparando'), ('enviada', 'Enviada'), ('entregada', 'Entregada'), ('cancelada', 'Cancelada')], default='creada', max_length=20)),
                ('notas', models.TextField(blank=True, null=True)),
                ('compra', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='orden', to='marketplace.compra')),
            ],
            options={
                'verbose_name': 'Orden',
                'verbose_name_plural': 'Órdenes',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]
