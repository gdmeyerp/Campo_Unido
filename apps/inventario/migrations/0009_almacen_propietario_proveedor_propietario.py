# Generated by Django 5.1.6 on 2025-03-13 05:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0008_pedidoproveedor_propietario'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='almacen',
            name='propietario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='almacenes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='proveedor',
            name='propietario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proveedores', to=settings.AUTH_USER_MODEL),
        ),
    ]
