# Simulation

## Lancement
python3 main.py

## Initialisation
Remplir le fichier init.json :
 * Caractérise la route : nom, longueur, sorties, bornes  
  
Remplir le fichier scenario.json :
 * Une ligne par voiture avec son heure de départ, km de départ, de sortie d'autoroute, autonomie en entré d'autoroute, ...
  
## Sortie
Resultat.print_log() Affiche le trajet de chaque voiture

Simulation.stat_time_per_voiture() : return  t_wait, t_charge, t_global   
 * t_wait = temps d'attente pour chaque voiture  
 * t_charge = temps de charge pour chaque voiture  
 * t_global = temps global pour chaque voiture
  
Simulation.stat_time_per_borne() : return  t_wait, t_use, t_global   
 * t_wait = temps d'attente cumulé par borne 
 * t_charge = temps de charge cumulé par borne 
 * t_global = durée de la simulation

Ensuite calculer ce qu'on a besoin dans Resultat
 * get_pourcentage_arret 

## Fonctionnement
On calcul le prochain évènement de la voiture ayant avancé le moins loin dans le temps.
Ce prochain évènemnt est soit :
 * "avance" : avancer jusqu'au prochain stop (station de charge ou sortie d'autoroute ou panne)
 * "wait" : attente de son tour à la station
 * "charge" : temps de charge dépendant de la distance à parcourir par la suite
On arrête une fois que toute les voitures ont dépassés le temps de fin de simulation.