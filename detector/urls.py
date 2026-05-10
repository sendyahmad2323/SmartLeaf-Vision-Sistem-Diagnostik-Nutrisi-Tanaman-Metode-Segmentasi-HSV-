from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit/<int:id>/', views.edit_deteksi, name='edit_deteksi'),
    path('hapus/<int:id>/', views.hapus_deteksi, name='hapus_deteksi'),
]