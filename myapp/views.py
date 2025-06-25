import urllib.parse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Capteur, Mesure
from django.utils.dateparse import parse_date
import csv
from django.utils.timezone import localtime
from datetime import datetime
from .forms import CapteurForm
import plotly.graph_objects as go
from collections import defaultdict
from datetime import datetime, timedelta


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
    mesures = Mesure.objects.all().order_by('date_heure')

    if not mesures.exists():
        return render(request, 'graphique.html', {
            'graph': "<p>Aucune mesure enregistrée dans la base de données.</p>"
        })

    # Regrouper les mesures par capteur
    groupes = defaultdict(lambda: {'dates': [], 'temperatures': []})

    for mesure in mesures:
        if not mesure.id_capteur:
            continue
        capteur_nom = mesure.id_capteur.nom_capteur
        groupes[capteur_nom]['dates'].append(localtime(mesure.date_heure))
        groupes[capteur_nom]['temperatures'].append(float(mesure.temperature))

    # Création du graphique
    fig = go.Figure()

    for capteur, data in groupes.items():
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['temperatures'],
            mode='lines+markers',
            name=capteur
        ))

    fig.update_layout(
        title={
            'text': "Toutes les mesures de température par capteur",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Date',
        yaxis_title='Température (°C)',
        xaxis=dict(
            showgrid=True,
            tickformat='%d %b %H:%M',
            tickangle=45
        ),
        yaxis=dict(
            showgrid=True,
            rangemode='tozero'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        template='plotly_white'
    )

    fig.update_traces(marker=dict(size=6))

    fig_html = fig.to_html(full_html=False)
    return render(request, 'graphique.html', {'graph': fig_html})