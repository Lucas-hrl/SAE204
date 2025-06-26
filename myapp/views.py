from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Capteur, Mesure
from django.utils.dateparse import parse_date
import csv
from django.utils.timezone import localtime
from .forms import CapteurForm
import plotly.graph_objects as go
from collections import defaultdict



def index(request):
    capteurs = Capteur.objects.all()
    mesures = Mesure.objects.all()

    capteurid = request.GET.get('capteur_id')
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')

    if capteurid:
        mesures = mesures.filter(id_capteur=capteurid)
    if date_start:
        mesures = mesures.filter(date_heure__gte=parse_date(date_start))
    if date_end:
        mesures = mesures.filter(date_heure__lte=parse_date(date_end))

    return render(request, 'index.html', {'capteurs': capteurs, 'mesures': mesures})




def delete_mesure(request, mesure_id):
    mesure = get_object_or_404(Mesure, pk=mesure_id)
    mesure.delete()
    return redirect('index')



def modifier_capteur(request, id_capteur):
    capteur = get_object_or_404(Capteur, id_capteur=id_capteur)

    if request.method == 'POST':
        form = CapteurForm(request.POST, instance=capteur)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirige vers la page principale ou liste des capteurs
    else:
        form = CapteurForm(instance=capteur)

    return render(request, 'modifier_capteur.html', {'form': form, 'capteur': capteur})



def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mesures.csv"'

    writer = csv.writer(response)
    writer.writerow(['MesureID', 'CapteurID', 'DateHeure', 'Température'])

    for mesure in Mesure.objects.all():
        writer.writerow([
            mesure.id_mesure,
            mesure.id_capteur.id_capteur,
            localtime(mesure.date_heure).strftime("%Y-%m-%d %H:%M:%S"),
            mesure.temperature
        ])

    return response


def graphique(request):
    mesures = Mesure.objects.select_related('id_capteur').all().order_by('date_heure')
    
    if not mesures.exists():
        return render(request, 'graphique.html', {
            'graph': "<div class='alert alert-info text-center p-4'><h5>Aucune données disponibles</h5><p>Aucune mesure enregistrée.</p></div>"
        })
    
    # Regroupement des données par capteur
    data_capteurs = defaultdict(lambda: {'dates': [], 'temperatures': [], 'nom': ''})
    
    for mesure in mesures:
        if mesure.id_capteur and mesure.temperature is not None:
            capteur_id = mesure.id_capteur.id_capteur
            capteur_nom = mesure.id_capteur.nom_capteur
            
            data_capteurs[capteur_id]['dates'].append(localtime(mesure.date_heure))
            data_capteurs[capteur_id]['temperatures'].append(float(mesure.temperature))
            data_capteurs[capteur_id]['nom'] = capteur_nom
    
    # Création du graphique
    fig = go.Figure()
    
    couleurs = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
    
    for i, (capteur_id, data) in enumerate(data_capteurs.items()):
        couleur = couleurs[i % len(couleurs)]
        
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['temperatures'],
            mode='lines+markers',
            name=data['nom'],
            line=dict(width=3, color=couleur),
            marker=dict(size=6, color=couleur),
            hovertemplate='<b>%{fullData.name}</b><br>Température: %{y:.1f}°C<br>%{x}<extra></extra>'
        ))
    
    # Configuration du layout
    fig.update_layout(
        title={
            'text': 'Évolution des Températures par Capteur',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis={
            'title': 'Date et Heure',
            'showgrid': True,
            'gridcolor': 'lightgray',
            'tickformat': '%d/%m %H:%M'
        },
        yaxis={
            'title': 'Température (°C)',
            'showgrid': True,
            'gridcolor': 'lightgray'
        },
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'right',
            'x': 1
        },
        height=600,
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='white',
        hovermode='x unified'
    )
    
    # Export HTML
    fig_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    return render(request, 'graphique.html', {'graph': fig_html})


def liste_capteurs(request):
    capteurs = Capteur.objects.all()
    return render(request, 'capteurs.html', {'capteurs': capteurs})

