import json
import datetime
import random


class Scenario:

    def __init__(self,scenario_file):
        self.n=0
        self.type_voiture = []
        self.type_trajet =[]
        self.proportion_trajet=[]
        self.scenario=dict()
        self.dt=datetime.timedelta(hours=1)
        self.repartition_voiture=[]
        self.proportion_voiture=[]

        self.generer_scenario_from_json(scenario_file)

    def generer_scenario_from_json(self,scenario_file):
        with open(scenario_file) as f:
            cara_scenario = json.load(f)

        self.nom = cara_scenario["nom"]
        self.n = cara_scenario["n_voiture"]
        self.duree=datetime.timedelta(hours=cara_scenario["duree"]["heure"],minutes=cara_scenario["duree"]["minute"])

        self.scenario["description"] = cara_scenario["nom"]
        self.scenario["duree"] = cara_scenario["duree"]
        self.scenario["Voitures"] = []

        self.repartition_voiture=cara_scenario["repartition_voiture"]

        for voiture in cara_scenario["type_voiture"]:
            self.type_voiture.append(voiture)
            self.proportion_voiture.append(voiture["proportion"])

        for trajet in cara_scenario["type_trajet"]:
            self.type_trajet.append(trajet)
        for propo_trajet in cara_scenario["proportion_trajet_par_heure"]:
            self.proportion_trajet.append(propo_trajet)


    def create_voiture(self,autonomie,km_start,km_end,km_after_end,time_start,autonomie_max,capacite):
        #{"autonomie": 50, "start": 10, "end": 100, "km_after_end": 0, "time_start": 0, "autonomie_max": 390,"capacite": 52},
        self.scenario["Voitures"].append({"autonomie": autonomie, "start": km_start, "end": km_end, "km_after_end": km_after_end, "time_start": time_start, "autonomie_max": autonomie_max,"capacite": capacite})

    def create_voitures_sur_dt(self,time,n_voitures,proportion_voiture,proportion_trajet):
        for voiture in range(n_voitures):
            autonomie = self.get_autonomie(50,300)
            km_start , km_end = self.get_trajet_type(proportion_trajet)
            km_after_end = self.get_km_after_end(5,400)
            time_start = self.get_time_start(time)
            autonomie_max, capacite = self.get_type_voiture(proportion_voiture)

            self.create_voiture(autonomie,km_start,km_end,km_after_end,time_start,autonomie_max,capacite)

    def get_type_voiture(self,proportion_voiture):
        indexList = [j for j in range(len(self.type_voiture))]

        i = random.choices(indexList,weights=proportion_voiture,k=1)[0]
        return (self.type_voiture[i]["autonomie_max"],self.type_voiture[i]["capacite"] )

    def get_trajet_type(self,proportion_trajet):
        indexList = [j for j in range(len(proportion_trajet))]

        i = random.choices(indexList,weights=proportion_trajet,k=1)[0]
        return (self.type_trajet[i]["km_start"],self.type_trajet[i]["km_end"] )

    def get_time_start(self,time):
        return random.randrange( round(time.total_seconds() / 60) ,round((time.total_seconds()+self.dt.total_seconds()) / 60),1)

    def get_km_after_end(self,inf,sup):
        return random.randrange(inf,sup,1)

    def get_autonomie(self,inf,sup):
        return random.randrange(inf,sup,1)

    def create_scenario_json(self):

        self.repartition_voiture = [ int(x*self.n) for x in self.repartition_voiture]

        for i in range(len(self.repartition_voiture)):
            self.create_voitures_sur_dt(datetime.timedelta(hours=i), self.repartition_voiture[i], self.proportion_voiture,self.proportion_trajet[i])

        with open('scenario/'+self.nom+'.json', 'w') as mon_fichier:
            json.dump(self.scenario, mon_fichier)

    def scenario_json_test_charge(self):
        n = 200000
        repartition_voiture=[ int(x*n) for x in [0.05,0.15,0.1,0.15,0.1,0.1,0.1,0.1,0.1,0.05]]
        #Complete pour 10 heures
        for i in range(10):
            self.create_voitures_sur_dt(datetime.timedelta(hours=i), repartition_voiture[i], [0.7, 0.3], [0.15,0.15,0.15,0.15,0.4])


        with open('scenario/'+self.nom+'.json', 'w') as mon_fichier:
            json.dump(self.scenario, mon_fichier)