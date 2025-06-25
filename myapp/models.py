from django.db import models

class Capteur(models.Model):
    id_capteur = models.CharField(primary_key=True, max_length=30)
    nom_capteur = models.CharField(max_length=100, unique=True)
    piece = models.CharField(max_length=50)
    emplacement = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'capteurs'
        managed = False

class Mesure(models.Model):
    id_mesure = models.AutoField(primary_key=True)
    id_capteur = models.ForeignKey(Capteur, to_field='id_capteur', on_delete=models.CASCADE, db_column='id_capteur')
    date_heure = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'mesures'
        managed = False
