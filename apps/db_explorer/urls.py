from django.urls import path
from . import views

app_name = 'db_explorer'

urlpatterns = [
    path('', views.index, name='index'),
    path('model/<str:app_label>/<str:model_name>/', views.model_list, name='model_list'),
    path('model/<str:app_label>/<str:model_name>/<int:record_id>/', views.record_detail, name='record_detail'),
    path('api/model/<str:app_label>/<str:model_name>/', views.api_model_data, name='api_model_data'),
    path('visualize/<str:app_label>/<str:model_name>/', views.visualize_data, name='visualize_data'),
    
    # URLs para CRUD
    path('model/<str:app_label>/<str:model_name>/create/', views.create_record, name='create_record'),
    path('model/<str:app_label>/<str:model_name>/<int:record_id>/edit/', views.edit_record, name='edit_record'),
    path('model/<str:app_label>/<str:model_name>/<int:record_id>/delete/', views.delete_record, name='delete_record'),
] 