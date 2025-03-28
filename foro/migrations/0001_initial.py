# Generated by Django 4.2.9 on 2024-10-11 01:55

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
            name='CategoriaForo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_categoria', models.CharField(max_length=255)),
                ('descripcion_categoria', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ComentarioPublicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido_comentario', models.TextField()),
                ('fecha_hora_comentario', models.DateTimeField(auto_now_add=True)),
                ('votos_positivos', models.IntegerField(default=0)),
                ('votos_negativos', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoComentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_estado', models.CharField(max_length=50)),
                ('descripcion_estado', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EstadoForo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_estado', models.CharField(max_length=50)),
                ('descripcion_estado', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EstadoPublicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_estado', models.CharField(max_length=50)),
                ('descripcion_estado', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EstadoReporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_estado', models.CharField(max_length=50)),
                ('descripcion_estado', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Foro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo_foro', models.CharField(max_length=255)),
                ('descripcion_foro', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.categoriaforo')),
                ('estado_foro', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='foro.estadoforo')),
            ],
        ),
        migrations.CreateModel(
            name='PublicacionForo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo_publicacion', models.CharField(max_length=255)),
                ('contenido_publicacion', models.TextField()),
                ('fecha_hora_publicacion', models.DateTimeField(auto_now_add=True)),
                ('votos_positivos', models.IntegerField(default=0)),
                ('votos_negativos', models.IntegerField(default=0)),
                ('estado_publicacion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='foro.estadopublicacion')),
                ('foro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.foro')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RolForo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_rol', models.CharField(max_length=50)),
                ('descripcion_rol', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TipoReaccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_reaccion', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='VotacionPublicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_voto', models.CharField(max_length=10)),
                ('fecha_hora_voto', models.DateTimeField(auto_now_add=True)),
                ('publicacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.publicacionforo')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VotacionComentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_voto', models.CharField(max_length=10)),
                ('fecha_hora_voto', models.DateTimeField(auto_now_add=True)),
                ('comentario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.comentariopublicacion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioRolForo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asignacion', models.DateTimeField(auto_now_add=True)),
                ('rol_foro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.rolforo')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReportePublicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motivo_reporte', models.TextField()),
                ('fecha_hora_reporte', models.DateTimeField(auto_now_add=True)),
                ('estado_reporte', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='foro.estadoreporte')),
                ('publicacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.publicacionforo')),
                ('usuario_reportador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReporteComentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motivo_reporte', models.TextField()),
                ('fecha_hora_reporte', models.DateTimeField(auto_now_add=True)),
                ('comentario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.comentariopublicacion')),
                ('estado_reporte', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='foro.estadoreporte')),
                ('usuario_reportador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReaccionPublicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora_reaccion', models.DateTimeField(auto_now_add=True)),
                ('publicacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.publicacionforo')),
                ('tipo_reaccion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='foro.tiporeaccion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReaccionComentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora_reaccion', models.DateTimeField(auto_now_add=True)),
                ('comentario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.comentariopublicacion')),
                ('tipo_reaccion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='foro.tiporeaccion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PuntuacionUsuarioForo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntaje', models.IntegerField(default=0)),
                ('nivel', models.CharField(max_length=50)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HistorialPuntuacionForo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accion', models.CharField(max_length=100)),
                ('puntos_obtenidos', models.IntegerField()),
                ('fecha_hora_accion', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comentariopublicacion',
            name='estado_comentario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='foro.estadocomentario'),
        ),
        migrations.AddField(
            model_name='comentariopublicacion',
            name='publicacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foro.publicacionforo'),
        ),
        migrations.AddField(
            model_name='comentariopublicacion',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
