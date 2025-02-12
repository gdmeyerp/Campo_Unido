# Generated by Django 4.2.9 on 2024-10-10 17:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ciudad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_ciudad', models.CharField(max_length=100)),
                ('tipo_zona', models.CharField(choices=[('Urbana', 'Urbana'), ('Rural', 'Rural'), ('Suburbana', 'Suburbana')], default='Urbana', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_pais', models.CharField(max_length=100)),
                ('codigo_iso', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ubicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(max_length=255)),
                ('codigo_postal', models.CharField(max_length=20)),
                ('latitud', models.FloatField()),
                ('longitud', models.FloatField()),
                ('altitud', models.FloatField(blank=True, null=True)),
                ('zona_horaria', models.CharField(max_length=50)),
                ('ciudad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ubicaciones.ciudad')),
            ],
        ),
        migrations.CreateModel(
            name='HistorialUbicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_cambio', models.CharField(choices=[('Creación', 'Creación'), ('Actualización', 'Actualización'), ('Eliminación', 'Eliminación')], max_length=50)),
                ('fecha_cambio', models.DateTimeField(auto_now_add=True)),
                ('detalles_cambio', models.TextField()),
                ('ubicacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ubicaciones.ubicacion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_estado', models.CharField(max_length=100)),
                ('pais', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ubicaciones.pais')),
            ],
        ),
        migrations.AddField(
            model_name='ciudad',
            name='estado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ubicaciones.estado'),
        ),
    ]
