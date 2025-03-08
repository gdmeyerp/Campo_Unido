from django.shortcuts import render, redirect, get_object_or_404
from django.apps import apps
from django.db import models, DatabaseError, OperationalError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.forms import modelform_factory
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import numpy as np
from django.conf import settings
import os
from django_pandas.io import read_frame
from django.urls import reverse

@login_required
def index(request):
    """Vista principal que muestra todas las aplicaciones y modelos"""
    app_models = {}
    
    # Lista de aplicaciones a excluir (sistema, autenticación, admin, etc.)
    excluded_apps = [
        'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
        'staticfiles', 'sites', 'foro_machina', 'machina', 'core'
    ]
    
    # Modelos específicos a excluir (aunque su app no esté completamente excluida)
    excluded_models = [
        'LogEntry', 'Permission', 'Group', 'User', 'ContentType', 
        'Session', 'Site', 'UserProfile', 'UserRoles',
        'PerfilUsuario', 'Forum', 'Topic', 'Post', 'ForumPermission',
        'ForumProfile', 'Attachment', 'ForumReadTrack', 'TopicReadTrack'
    ]
    
    # Obtener todas las aplicaciones y sus modelos
    for app_config in apps.get_app_configs():
        # Saltar las aplicaciones excluidas
        if app_config.label in excluded_apps or app_config.name.startswith('django.contrib'):
            continue
            
        models_list = []
        for model in app_config.get_models():
            # Saltar los modelos excluidos explícitamente
            if model.__name__ in excluded_models:
                continue
                
            try:
                # Intentar contar registros, pero manejar errores si la tabla no existe
                count = model.objects.count()
            except (DatabaseError, OperationalError):
                # Si la tabla no existe, mostrar un mensaje en lugar del conteo
                count = "Tabla no creada"
            
            models_list.append({
                'name': model.__name__,
                'verbose_name': model._meta.verbose_name.title(),
                'count': count,
                'url': f'/db-explorer/model/{app_config.label}/{model.__name__}/'
            })
        
        if models_list:
            app_models[app_config.verbose_name] = {
                'name': app_config.name,
                'label': app_config.label,
                'models': models_list
            }
    
    context = {
        'app_models': app_models,
        'title': 'Explorador de Base de Datos'
    }
    
    return render(request, 'db_explorer/index.html', context)

@login_required
def model_list(request, app_label, model_name):
    """Vista que muestra los registros de un modelo específico"""
    # Lista de aplicaciones a excluir
    excluded_apps = [
        'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
        'staticfiles', 'sites', 'foro_machina', 'machina', 'core'
    ]
    
    # Modelos específicos a excluir
    excluded_models = [
        'LogEntry', 'Permission', 'Group', 'User', 'ContentType', 
        'Session', 'Site', 'UserProfile', 'UserRoles',
        'PerfilUsuario', 'Forum', 'Topic', 'Post', 'ForumPermission',
        'ForumProfile', 'Attachment', 'ForumReadTrack', 'TopicReadTrack'
    ]
    
    # Verificar si el modelo solicitado está en la lista de exclusión
    if app_label in excluded_apps or model_name in excluded_models:
        context = {
            'error_title': 'Acceso Restringido',
            'error_message': 'No tiene permiso para ver este modelo ya que pertenece a la configuración del sistema.',
            'title': 'Error de Acceso'
        }
        return render(request, 'db_explorer/error.html', context, status=403)
    
    try:
        # Obtener el modelo
        model = apps.get_model(app_label, model_name)
        
        # Verificar si el modelo pertenece a una app de Django
        if model._meta.app_config.name.startswith('django.contrib'):
            context = {
                'error_title': 'Acceso Restringido',
                'error_message': 'No tiene permiso para ver este modelo ya que pertenece a la configuración del sistema.',
                'title': 'Error de Acceso'
            }
            return render(request, 'db_explorer/error.html', context, status=403)
        
        # Obtener parámetros de filtrado y ordenamiento
        search_term = request.GET.get('search', '')
        order_by = request.GET.get('order_by', 'id')
        page = request.GET.get('page', 1)
        
        try:
            # Obtener todos los registros
            queryset = model.objects.all()
            
            # Aplicar búsqueda si se proporciona un término
            if search_term:
                # Construir filtros para campos de texto
                search_filters = models.Q()
                for field in model._meta.fields:
                    if isinstance(field, (models.CharField, models.TextField)):
                        search_filters |= models.Q(**{f"{field.name}__icontains": search_term})
                
                queryset = queryset.filter(search_filters)
            
            # Aplicar ordenamiento
            if order_by.startswith('-'):
                order_field = order_by[1:]
                if order_field in [f.name for f in model._meta.fields]:
                    queryset = queryset.order_by(order_by)
            else:
                if order_by in [f.name for f in model._meta.fields]:
                    queryset = queryset.order_by(order_by)
            
            # Paginación
            paginator = Paginator(queryset, 20)  # 20 registros por página
            page_obj = paginator.get_page(page)
        except (DatabaseError, OperationalError):
            # Si la tabla no existe, mostrar un mensaje
            queryset = []
            paginator = Paginator(queryset, 20)
            page_obj = paginator.get_page(1)
        
        # Obtener información de los campos
        fields = []
        for field in model._meta.fields:
            fields.append({
                'name': field.name,
                'verbose_name': field.verbose_name.title(),
                'type': field.get_internal_type(),
                'is_relation': field.is_relation
            })
        
        context = {
            'model': model.__name__,
            'app_label': app_label,
            'verbose_name': model._meta.verbose_name.title(),
            'verbose_name_plural': model._meta.verbose_name_plural.title(),
            'fields': fields,
            'page_obj': page_obj,
            'search_term': search_term,
            'order_by': order_by,
            'title': f'Registros de {model._meta.verbose_name_plural.title()}',
            'table_exists': True
        }
        
        return render(request, 'db_explorer/model_list.html', context)
    
    except (DatabaseError, OperationalError):
        context = {
            'model': model_name,
            'app_label': app_label,
            'table_exists': False,
            'title': f'Tabla no disponible para {model_name}'
        }
        return render(request, 'db_explorer/model_list.html', context)
    except LookupError:
        return HttpResponse(f"Modelo {model_name} no encontrado en la aplicación {app_label}", status=404)

@login_required
def record_detail(request, app_label, model_name, record_id):
    """Vista que muestra el detalle de un registro específico"""
    # Lista de aplicaciones a excluir
    excluded_apps = [
        'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
        'staticfiles', 'sites', 'foro_machina', 'machina', 'core'
    ]
    
    # Modelos específicos a excluir
    excluded_models = [
        'LogEntry', 'Permission', 'Group', 'User', 'ContentType', 
        'Session', 'Site', 'UserProfile', 'UserRoles',
        'PerfilUsuario', 'Forum', 'Topic', 'Post', 'ForumPermission',
        'ForumProfile', 'Attachment', 'ForumReadTrack', 'TopicReadTrack'
    ]
    
    # Verificar si el modelo solicitado está en la lista de exclusión
    if app_label in excluded_apps or model_name in excluded_models:
        context = {
            'error_title': 'Acceso Restringido',
            'error_message': 'No tiene permiso para ver este registro ya que pertenece a la configuración del sistema.',
            'title': 'Error de Acceso'
        }
        return render(request, 'db_explorer/error.html', context, status=403)
        
    try:
        # Obtener el modelo y el registro
        model = apps.get_model(app_label, model_name)
        
        # Verificar si el modelo pertenece a una app de Django
        if model._meta.app_config.name.startswith('django.contrib'):
            context = {
                'error_title': 'Acceso Restringido',
                'error_message': 'No tiene permiso para ver este registro ya que pertenece a la configuración del sistema.',
                'title': 'Error de Acceso'
            }
            return render(request, 'db_explorer/error.html', context, status=403)
            
        record = model.objects.get(pk=record_id)
        
        # Obtener información de los campos y sus valores
        fields_data = []
        for field in model._meta.fields:
            value = getattr(record, field.name)
            
            # Formatear el valor según el tipo de campo
            if field.is_relation and value is not None:
                related_app = value._meta.app_label
                related_model = value.__class__.__name__
                related_url = f'/db-explorer/model/{related_app}/{related_model}/{value.pk}/'
                
                fields_data.append({
                    'name': field.name,
                    'verbose_name': field.verbose_name.title(),
                    'value': str(value),
                    'is_relation': True,
                    'related_url': related_url
                })
            else:
                fields_data.append({
                    'name': field.name,
                    'verbose_name': field.verbose_name.title(),
                    'value': value,
                    'is_relation': False
                })
        
        # Obtener relaciones inversas (ForeignKey, OneToOne, ManyToMany)
        related_objects = []
        for relation in model._meta.related_objects:
            related_model = relation.related_model
            related_name = relation.get_accessor_name()
            
            try:
                if relation.one_to_many or relation.many_to_many:
                    # Relación uno a muchos o muchos a muchos
                    related_queryset = getattr(record, related_name).all()
                    if related_queryset.exists():
                        related_objects.append({
                            'name': related_name,
                            'verbose_name': related_model._meta.verbose_name_plural.title(),
                            'count': related_queryset.count(),
                            'model': related_model.__name__,
                            'app_label': related_model._meta.app_label,
                            'type': 'many'
                        })
                elif relation.one_to_one:
                    # Relación uno a uno
                    try:
                        related_obj = getattr(record, related_name)
                        if related_obj:
                            related_objects.append({
                                'name': related_name,
                                'verbose_name': related_model._meta.verbose_name.title(),
                                'model': related_model.__name__,
                                'app_label': related_model._meta.app_label,
                                'id': related_obj.pk,
                                'type': 'one'
                            })
                    except related_model.DoesNotExist:
                        pass
            except Exception as e:
                # Ignorar errores en relaciones
                pass
        
        context = {
            'model': model.__name__,
            'app_label': app_label,
            'verbose_name': model._meta.verbose_name.title(),
            'record': record,
            'fields': fields_data,
            'related_objects': related_objects,
            'title': f'Detalle de {model._meta.verbose_name.title()}'
        }
        
        return render(request, 'db_explorer/record_detail.html', context)
    
    except model.DoesNotExist:
        return HttpResponse(f"Registro con ID {record_id} no encontrado", status=404)
    except LookupError:
        return HttpResponse(f"Modelo {model_name} no encontrado en la aplicación {app_label}", status=404)

@login_required
def api_model_data(request, app_label, model_name):
    """API para obtener datos de un modelo en formato JSON"""
    # Lista de aplicaciones a excluir
    excluded_apps = [
        'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
        'staticfiles', 'sites', 'foro_machina', 'machina', 'core'
    ]
    
    # Modelos específicos a excluir
    excluded_models = [
        'LogEntry', 'Permission', 'Group', 'User', 'ContentType', 
        'Session', 'Site', 'UserProfile', 'UserRoles',
        'PerfilUsuario', 'Forum', 'Topic', 'Post', 'ForumPermission',
        'ForumProfile', 'Attachment', 'ForumReadTrack', 'TopicReadTrack'
    ]
    
    # Verificar si el modelo solicitado está en la lista de exclusión
    if app_label in excluded_apps or model_name in excluded_models:
        return JsonResponse({"error": "No tiene permiso para acceder a estos datos"}, status=403)
        
    try:
        model = apps.get_model(app_label, model_name)
        
        # Verificar si el modelo pertenece a una app de Django
        if model._meta.app_config.name.startswith('django.contrib'):
            return JsonResponse({"error": "No tiene permiso para acceder a estos datos"}, status=403)
        
        # Parámetros de paginación
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # Obtener registros
        queryset = model.objects.all()
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Convertir a lista de diccionarios
        data = []
        for obj in page_obj:
            item = {}
            for field in model._meta.fields:
                value = getattr(obj, field.name)
                
                # Convertir a formato serializable
                if isinstance(value, models.Model):
                    item[field.name] = str(value)
                else:
                    item[field.name] = value
            
            data.append(item)
        
        response = {
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'results': data
        }
        
        return JsonResponse(response)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def visualize_data(request, app_label, model_name):
    """Vista para visualizar datos del modelo utilizando pandas y matplotlib"""
    # Lista de aplicaciones a excluir
    excluded_apps = [
        'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
        'staticfiles', 'sites', 'foro_machina', 'machina', 'core'
    ]
    
    # Modelos específicos a excluir
    excluded_models = [
        'LogEntry', 'Permission', 'Group', 'User', 'ContentType', 
        'Session', 'Site', 'UserProfile', 'UserRoles',
        'PerfilUsuario', 'Forum', 'Topic', 'Post', 'ForumPermission',
        'ForumProfile', 'Attachment', 'ForumReadTrack', 'TopicReadTrack'
    ]
    
    # Verificar si el modelo solicitado está en la lista de exclusión
    if app_label in excluded_apps or model_name in excluded_models:
        context = {
            'error_title': 'Acceso Restringido',
            'error_message': 'No tiene permiso para visualizar datos de este modelo ya que pertenece a la configuración del sistema.',
            'title': 'Error de Acceso'
        }
        return render(request, 'db_explorer/error.html', context, status=403)
    
    try:
        # Configurar matplotlib para no usar GUI
        matplotlib.use('Agg')
        
        # Obtener el modelo
        model = apps.get_model(app_label, model_name)
        
        # Verificar si el modelo pertenece a una app de Django
        if model._meta.app_config.name.startswith('django.contrib'):
            context = {
                'error_title': 'Acceso Restringido',
                'error_message': 'No tiene permiso para visualizar datos de este modelo ya que pertenece a la configuración del sistema.',
                'title': 'Error de Acceso'
            }
            return render(request, 'db_explorer/error.html', context, status=403)
        
        # Obtener los datos del modelo
        queryset = model.objects.all()
        
        # Si no hay datos, mostrar mensaje
        if not queryset.exists():
            context = {
                'model': model.__name__,
                'app_label': app_label,
                'verbose_name': model._meta.verbose_name.title(),
                'verbose_name_plural': model._meta.verbose_name_plural.title(),
                'title': f'Visualización de {model._meta.verbose_name_plural.title()}',
                'error_message': 'No hay datos disponibles para visualizar.'
            }
            return render(request, 'db_explorer/data_visualization.html', context)
        
        # Convertir queryset a DataFrame de pandas
        df = read_frame(queryset)
        
        # Identificar columnas numéricas para análisis estadístico
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Si no hay columnas numéricas, mostrar mensaje
        if not numeric_columns:
            context = {
                'model': model.__name__,
                'app_label': app_label,
                'verbose_name': model._meta.verbose_name.title(),
                'verbose_name_plural': model._meta.verbose_name_plural.title(),
                'title': f'Visualización de {model._meta.verbose_name_plural.title()}',
                'error_message': 'Este modelo no tiene campos numéricos para visualizar.'
            }
            return render(request, 'db_explorer/data_visualization.html', context)
        
        # Generar estadísticas descriptivas
        summary_stats = {
            'Conteo': df[numeric_columns].count().values.tolist(),
            'Media': df[numeric_columns].mean().round(2).values.tolist(),
            'Mediana': df[numeric_columns].median().round(2).values.tolist(),
            'Mínimo': df[numeric_columns].min().values.tolist(),
            'Máximo': df[numeric_columns].max().values.tolist(),
            'Desv. Estándar': df[numeric_columns].std().round(2).values.tolist()
        }
        
        # Función para generar gráficos y convertirlos a base64
        def get_image_base64(fig):
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()
            plt.close(fig)
            return f'data:image/png;base64,{img_str}'
        
        # Generar gráfico de torta para la primera columna categórica si existe
        chart_pie_url = None
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_columns:
            column = categorical_columns[0]
            # Limitar a las 10 categorías más frecuentes
            value_counts = df[column].value_counts().nlargest(10)
            
            if not value_counts.empty:
                fig, ax = plt.subplots(figsize=(8, 6))
                value_counts.plot.pie(autopct='%1.1f%%', ax=ax, shadow=True)
                ax.set_title(f'Distribución de {column}')
                ax.set_ylabel('')
                chart_pie_url = get_image_base64(fig)
        
        # Generar gráfico de barras para la primera columna numérica
        chart_bar_url = None
        if numeric_columns:
            column = numeric_columns[0]
            fig, ax = plt.subplots(figsize=(10, 6))
            df[column].plot.bar(ax=ax)
            ax.set_title(f'Valores de {column}')
            ax.set_ylabel(column)
            ax.set_xlabel('Índice')
            chart_bar_url = get_image_base64(fig)
        
        # Generar gráfico de línea si hay 2 o más columnas numéricas
        chart_line_url = None
        if len(numeric_columns) >= 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            for column in numeric_columns[:3]:  # Limitar a las primeras 3 columnas
                df[column].plot.line(ax=ax, label=column)
            ax.set_title('Comparación de Valores Numéricos')
            ax.set_xlabel('Índice')
            ax.set_ylabel('Valor')
            ax.legend()
            chart_line_url = get_image_base64(fig)
        
        # Generar matriz de correlación si hay 2 o más columnas numéricas
        correlation_matrix_url = None
        if len(numeric_columns) >= 2:
            corr_matrix = df[numeric_columns].corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(corr_matrix, cmap='coolwarm')
            ax.set_title('Matriz de Correlación')
            
            # Añadir etiquetas a los ejes
            ax.set_xticks(np.arange(len(numeric_columns)))
            ax.set_yticks(np.arange(len(numeric_columns)))
            ax.set_xticklabels(numeric_columns, rotation=45, ha='right')
            ax.set_yticklabels(numeric_columns)
            
            # Añadir valores en cada celda
            for i in range(len(numeric_columns)):
                for j in range(len(numeric_columns)):
                    text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                                ha='center', va='center', color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black')
            
            plt.colorbar(im)
            fig.tight_layout()
            correlation_matrix_url = get_image_base64(fig)
        
        # Preparar contexto para la plantilla
        context = {
            'model': model.__name__,
            'app_label': app_label,
            'verbose_name': model._meta.verbose_name.title(),
            'verbose_name_plural': model._meta.verbose_name_plural.title(),
            'columns': numeric_columns,
            'summary_stats': summary_stats,
            'chart_pie_url': chart_pie_url,
            'chart_bar_url': chart_bar_url,
            'chart_line_url': chart_line_url,
            'correlation_matrix_url': correlation_matrix_url,
            'title': f'Visualización de {model._meta.verbose_name_plural.title()}'
        }
        
        return render(request, 'db_explorer/data_visualization.html', context)
    
    except Exception as e:
        context = {
            'error_title': 'Error de Visualización',
            'error_message': f'No se pudieron generar las visualizaciones: {str(e)}',
            'title': 'Error'
        }
        return render(request, 'db_explorer/error.html', context, status=500)

@login_required
def create_record(request, app_label, model_name):
    """Vista para crear un nuevo registro"""
    # Lista de aplicaciones a excluir
    excluded_apps = [
        'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
        'staticfiles', 'sites', 'foro_machina', 'machina', 'core'
    ]
    
    # Modelos específicos a excluir
    excluded_models = [
        'LogEntry', 'Permission', 'Group', 'User', 'ContentType', 
        'Session', 'Site', 'UserProfile', 'UserRoles',
        'PerfilUsuario', 'Forum', 'Topic', 'Post', 'ForumPermission',
        'ForumProfile', 'Attachment', 'ForumReadTrack', 'TopicReadTrack'
    ]
    
    # Verificar si el modelo solicitado está en la lista de exclusión
    if app_label in excluded_apps or model_name in excluded_models:
        context = {
            'error_title': 'Acceso Restringido',
            'error_message': 'No tiene permiso para crear registros en este modelo ya que pertenece a la configuración del sistema.',
            'title': 'Error de Acceso'
        }
        return render(request, 'db_explorer/error.html', context, status=403)
    
    try:
        # Obtener el modelo
        model = apps.get_model(app_label, model_name)
        
        # Verificar si el modelo pertenece a una app de Django
        if model._meta.app_config.name.startswith('django.contrib'):
            context = {
                'error_title': 'Acceso Restringido',
                'error_message': 'No tiene permiso para crear registros en este modelo ya que pertenece a la configuración del sistema.',
                'title': 'Error de Acceso'
            }
            return render(request, 'db_explorer/error.html', context, status=403)
        
        # Crear un formulario dinámico para el modelo
        ModelForm = modelform_factory(model, fields='__all__')
        
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, f'El registro de {model._meta.verbose_name} ha sido creado con éxito.')
                return redirect('db_explorer:model_list', app_label=app_label, model_name=model_name)
        else:
            form = ModelForm()
        
        context = {
            'form': form,
            'model': model_name,
            'app_label': app_label,
            'verbose_name': model._meta.verbose_name.title(),
            'verbose_name_plural': model._meta.verbose_name_plural.title(),
            'is_edit': False,
            'title': f'Nuevo {model._meta.verbose_name.title()}'
        }
        
        return render(request, 'db_explorer/record_form.html', context)
    
    except LookupError:
        return HttpResponse(f"Modelo {model_name} no encontrado en la aplicación {app_label}", status=404)
    except Exception as e:
        context = {
            'error_title': 'Error al Crear Registro',
            'error_message': str(e),
            'title': 'Error'
        }
        return render(request, 'db_explorer/error.html', context, status=500)

@login_required
def edit_record(request, app_label, model_name, record_id):
    """Vista para editar un registro existente"""
    # Lista de aplicaciones a excluir
    excluded_apps = [
        'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
        'staticfiles', 'sites', 'foro_machina', 'machina', 'core'
    ]
    
    # Modelos específicos a excluir
    excluded_models = [
        'LogEntry', 'Permission', 'Group', 'User', 'ContentType', 
        'Session', 'Site', 'UserProfile', 'UserRoles',
        'PerfilUsuario', 'Forum', 'Topic', 'Post', 'ForumPermission',
        'ForumProfile', 'Attachment', 'ForumReadTrack', 'TopicReadTrack'
    ]
    
    # Verificar si el modelo solicitado está en la lista de exclusión
    if app_label in excluded_apps or model_name in excluded_models:
        context = {
            'error_title': 'Acceso Restringido',
            'error_message': 'No tiene permiso para editar registros de este modelo ya que pertenece a la configuración del sistema.',
            'title': 'Error de Acceso'
        }
        return render(request, 'db_explorer/error.html', context, status=403)
    
    try:
        # Obtener el modelo y el registro
        model = apps.get_model(app_label, model_name)
        
        # Verificar si el modelo pertenece a una app de Django
        if model._meta.app_config.name.startswith('django.contrib'):
            context = {
                'error_title': 'Acceso Restringido',
                'error_message': 'No tiene permiso para editar registros de este modelo ya que pertenece a la configuración del sistema.',
                'title': 'Error de Acceso'
            }
            return render(request, 'db_explorer/error.html', context, status=403)
        
        # Obtener el registro o devolver 404
        record = get_object_or_404(model, pk=record_id)
        
        # Crear un formulario dinámico para el modelo
        ModelForm = modelform_factory(model, fields='__all__')
        
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=record)
            if form.is_valid():
                form.save()
                messages.success(request, f'El registro de {model._meta.verbose_name} ha sido actualizado con éxito.')
                return redirect('db_explorer:record_detail', app_label=app_label, model_name=model_name, record_id=record_id)
        else:
            form = ModelForm(instance=record)
        
        context = {
            'form': form,
            'model': model_name,
            'app_label': app_label,
            'verbose_name': model._meta.verbose_name.title(),
            'verbose_name_plural': model._meta.verbose_name_plural.title(),
            'is_edit': True,
            'record_id': record_id,
            'title': f'Editar {model._meta.verbose_name.title()}'
        }
        
        return render(request, 'db_explorer/record_form.html', context)
    
    except model.DoesNotExist:
        return HttpResponse(f"Registro con ID {record_id} no encontrado", status=404)
    except LookupError:
        return HttpResponse(f"Modelo {model_name} no encontrado en la aplicación {app_label}", status=404)
    except Exception as e:
        context = {
            'error_title': 'Error al Editar Registro',
            'error_message': str(e),
            'title': 'Error'
        }
        return render(request, 'db_explorer/error.html', context, status=500)

@login_required
def delete_record(request, app_label, model_name, record_id):
    """Vista para eliminar un registro"""
    # Lista de aplicaciones a excluir
    excluded_apps = [
        'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
        'staticfiles', 'sites', 'foro_machina', 'machina', 'core'
    ]
    
    # Modelos específicos a excluir
    excluded_models = [
        'LogEntry', 'Permission', 'Group', 'User', 'ContentType', 
        'Session', 'Site', 'UserProfile', 'UserRoles',
        'PerfilUsuario', 'Forum', 'Topic', 'Post', 'ForumPermission',
        'ForumProfile', 'Attachment', 'ForumReadTrack', 'TopicReadTrack'
    ]
    
    # Verificar si el modelo solicitado está en la lista de exclusión
    if app_label in excluded_apps or model_name in excluded_models:
        context = {
            'error_title': 'Acceso Restringido',
            'error_message': 'No tiene permiso para eliminar registros de este modelo ya que pertenece a la configuración del sistema.',
            'title': 'Error de Acceso'
        }
        return render(request, 'db_explorer/error.html', context, status=403)
    
    try:
        # Obtener el modelo y el registro
        model = apps.get_model(app_label, model_name)
        
        # Verificar si el modelo pertenece a una app de Django
        if model._meta.app_config.name.startswith('django.contrib'):
            context = {
                'error_title': 'Acceso Restringido',
                'error_message': 'No tiene permiso para eliminar registros de este modelo ya que pertenece a la configuración del sistema.',
                'title': 'Error de Acceso'
            }
            return render(request, 'db_explorer/error.html', context, status=403)
        
        # Obtener el registro o devolver 404
        record = get_object_or_404(model, pk=record_id)
        
        # Si es una solicitud POST, eliminar el registro
        if request.method == 'POST':
            try:
                record.delete()
                messages.success(request, f'El registro de {model._meta.verbose_name} ha sido eliminado con éxito.')
                return redirect('db_explorer:model_list', app_label=app_label, model_name=model_name)
            except Exception as e:
                messages.error(request, f'Error al eliminar: {str(e)}')
                return redirect('db_explorer:record_detail', app_label=app_label, model_name=model_name, record_id=record_id)
        
        # Obtener información de los campos y sus valores para mostrar en la confirmación
        fields_data = []
        for field in model._meta.fields:
            value = getattr(record, field.name)
            
            # Formatear el valor según el tipo de campo
            if field.is_relation and value is not None:
                fields_data.append({
                    'name': field.name,
                    'verbose_name': field.verbose_name.title(),
                    'value': str(value),
                    'is_relation': True
                })
            else:
                fields_data.append({
                    'name': field.name,
                    'verbose_name': field.verbose_name.title(),
                    'value': value,
                    'is_relation': False
                })
        
        # Obtener relaciones inversas (ForeignKey, OneToOne, ManyToMany)
        related_objects = []
        for relation in model._meta.related_objects:
            related_model = relation.related_model
            related_name = relation.get_accessor_name()
            
            try:
                if relation.one_to_many or relation.many_to_many:
                    # Relación uno a muchos o muchos a muchos
                    related_queryset = getattr(record, related_name).all()
                    if related_queryset.exists():
                        related_objects.append({
                            'name': related_name,
                            'verbose_name': related_model._meta.verbose_name_plural.title(),
                            'count': related_queryset.count(),
                            'model': related_model.__name__,
                            'app_label': related_model._meta.app_label,
                            'type': 'many'
                        })
                elif relation.one_to_one:
                    # Relación uno a uno
                    try:
                        related_obj = getattr(record, related_name)
                        if related_obj:
                            related_objects.append({
                                'name': related_name,
                                'verbose_name': related_model._meta.verbose_name.title(),
                                'model': related_model.__name__,
                                'app_label': related_model._meta.app_label,
                                'id': related_obj.pk,
                                'type': 'one'
                            })
                    except related_model.DoesNotExist:
                        pass
            except Exception:
                # Ignorar errores en relaciones
                pass
        
        context = {
            'model': model.__name__,
            'app_label': app_label,
            'verbose_name': model._meta.verbose_name.title(),
            'verbose_name_plural': model._meta.verbose_name_plural.title(),
            'record': record,
            'fields': fields_data,
            'related_objects': related_objects,
            'title': f'Eliminar {model._meta.verbose_name.title()}'
        }
        
        return render(request, 'db_explorer/delete_confirm.html', context)
    
    except model.DoesNotExist:
        return HttpResponse(f"Registro con ID {record_id} no encontrado", status=404)
    except LookupError:
        return HttpResponse(f"Modelo {model_name} no encontrado en la aplicación {app_label}", status=404)
    except Exception as e:
        context = {
            'error_title': 'Error al Eliminar Registro',
            'error_message': str(e),
            'title': 'Error'
        }
        return render(request, 'db_explorer/error.html', context, status=500)
