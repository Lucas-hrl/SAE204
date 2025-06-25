from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete/<int:mesure_id>/', views.delete_mesure, name='delete_mesure'),
    #path('edit/<str:capteur_id>/', views.edit_capteur_ajax, name='edit_capteur_ajax'),
    path('graphique/', views.graphique, name='graphique'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('capteur/<str:id_capteur>/modifier/', views.modifier_capteur, name='modifier_capteur'),

]
