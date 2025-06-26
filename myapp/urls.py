from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete/<int:mesure_id>/', views.delete_mesure, name='delete_mesure'),
    path('graphique/', views.graphique, name='graphique'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('capteur/<str:id_capteur>/modifier/', views.modifier_capteur, name='modifier_capteur'),
    path('capteurs/', views.liste_capteurs, name='liste_capteurs'),

]

