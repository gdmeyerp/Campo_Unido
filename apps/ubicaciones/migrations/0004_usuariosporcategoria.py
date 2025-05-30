# Generated by Django 5.1.6 on 2025-04-29 15:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        ('ubicaciones', '0003_datos_iniciales_colombia'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UsuariosPorCategoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ultima_actualizacion', models.DateTimeField(auto_now=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.categoriaproducto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['categoria', 'usuario'], name='ubicaciones_categor_4fb823_idx')],
                'unique_together': {('categoria', 'usuario')},
            },
        ),
    ]
