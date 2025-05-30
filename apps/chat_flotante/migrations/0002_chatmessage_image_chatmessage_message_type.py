# Generated by Django 5.1.6 on 2025-03-12 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_flotante', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='chat_images/', verbose_name='Imagen'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='message_type',
            field=models.CharField(choices=[('text', 'Texto'), ('image', 'Imagen')], default='text', max_length=10, verbose_name='Tipo de mensaje'),
        ),
    ]
