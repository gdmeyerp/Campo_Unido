# Generated by Django 5.1.6 on 2025-03-12 15:42

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
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Nombre')),
                ('is_group', models.BooleanField(default=False, verbose_name='Es grupo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última actualización')),
                ('participants', models.ManyToManyField(related_name='chat_rooms_flotante', to=settings.AUTH_USER_MODEL, verbose_name='Participantes')),
            ],
            options={
                'verbose_name': 'Sala de Chat',
                'verbose_name_plural': 'Salas de Chat',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Contenido')),
                ('is_read', models.BooleanField(default=False, verbose_name='Leído')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages_flotante', to=settings.AUTH_USER_MODEL, verbose_name='Remitente')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat_flotante.chatroom', verbose_name='Sala')),
            ],
            options={
                'verbose_name': 'Mensaje de Chat',
                'verbose_name_plural': 'Mensajes de Chat',
                'ordering': ['created_at'],
            },
        ),
    ]
