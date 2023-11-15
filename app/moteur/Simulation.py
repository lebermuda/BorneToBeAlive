import app.moteur.Route as Route
import app.moteur.Sortie as Sortie
import app.moteur.Borne as Borne
import app.moteur.Voiture as Voiture
import app.moteur.Scenario as Scenario
import json
from datetime import datetime, timedelta


class Simulation:

    def __init__(self, init_file, scenario, init_scenario):
        self.time = datetime.today()
        self.time_end = None
        self.time_start = self.time
        self.etats = dict()
        self.route = None

        self.n_voiture = None
        self.voitures = []

        self.initRoute(init_file)

        self.initBorne(scenario.stations)
        self.bornes = self.route.get_bornes()

        if init_scenario != None:
            self.initScenarioFromJSON(init_scenario)
        else:
            self.initScenarioFromFront(scenario)

    def initRoute(self, init_file):
        with open(init_file) as f:
            init = json.load(f)

        # init des caractéristique de la A6
        self.route = Route.Route(init['Route']['nom'], init['Route']['km'])

        # Ajout des sorties
        for sortie in init["Sorties"]:
            self.route.add_etape(Sortie.Sortie(sortie["nom"], sortie["location"], sortie["numero"]))

    def initBorne(self, bornes):
        # Ajout des Bornes
        for borne in bornes:
            puissances = []
            for i in range(int(borne["station_typeA"])):
                puissances.append(250)
            for i in range(int(borne["station_typeB"])):
                puissances.append(150)

            self.route.add_etape(Borne.Borne(int(borne["emplacement"]), puissances))

    def initScenarioFromJSON(self, scenario_file):
        with open(scenario_file) as f:
            scenario = json.load(f)

        self.n_voiture = len(scenario["Voitures"])
        self.time_end = self.time + timedelta(hours=scenario["duree"]["heure"], minutes=scenario["duree"]["minute"])

        for voiture in scenario["Voitures"]:
            time_start_voiture = self.time + timedelta(minutes=voiture["time_start"])
            voiture = Voiture.Voiture(voiture["autonomie"],
                                      voiture["start"],
                                      time_start_voiture,
                                      voiture["end"],
                                      voiture["km_after_end"],
                                      voiture["autonomie_max"],
                                      voiture["capacite"])

            self.voitures.append(voiture)

            if (time_start_voiture not in self.etats):
                self.etats[time_start_voiture] = [voiture]
            else:
                self.etats[time_start_voiture].append(voiture)

    def initScenarioFromFront(self, scenario):
        self.n_voiture = scenario.n_voitures
        self.time_end = self.time + timedelta(hours=scenario.h, minutes=scenario.min)

        build = Scenario.Scenario()
        res = build.create_scenario_front(scenario)

        for voiture in res["Voitures"]:

            time_start_voiture = self.time + timedelta(minutes=voiture["time_start"])
            voiture = Voiture.Voiture(voiture["autonomie"],
                                      voiture["start"],
                                      time_start_voiture,
                                      voiture["end"],
                                      voiture["km_after_end"],
                                      voiture["autonomie_max"],
                                      voiture["capacite"])

            self.voitures.append(voiture)

            if (time_start_voiture not in self.etats):
                self.etats[time_start_voiture] = [voiture]
            else:
                self.etats[time_start_voiture].append(voiture)

    def run_simulation(self):
        while (self.time < self.time_end):
            voiture = self.get_voiture_plus_tot()
            if (voiture == None):
                break

            time_next_state = self.get_time_of_next_step(voiture)

            # Si on sort ou qu'on dépasse le temps de simulation
            if voiture.location == voiture.end:  # or voiture.time+time_next_state > self.time_end :
                voiture.time = min(voiture.time + time_next_state, self.time_end)
                voiture.log.append(("end", voiture.time, voiture.location))

            elif time_next_state != None:

                voiture.time += time_next_state
                if (self.time_end > voiture.time):
                    if (voiture.time not in self.etats):
                        self.etats[voiture.time] = [voiture]
                    else:
                        self.etats[voiture.time].append(voiture)

    def get_time_of_next_step(self, voiture):
        if (voiture.in_charge):

            autonomie_desire = voiture.get_dist_to_next_stop(self.route)

            t_wait, t_charge = voiture.get_time_to_wait_and_charge(self.route.etapes[voiture.location],
                                                                   autonomie_desire, self.time_end)
            temps = t_wait + t_charge
            voiture.in_charge = False

            if temps != None and temps != -1:
                if voiture.time + t_wait < self.time_end:
                    if t_wait.total_seconds() > 0:
                        voiture.log.append(("wait", voiture.time + t_wait, voiture.location))
                        self.route.etapes[voiture.location].t_wait += t_wait
                        voiture.t_wait += t_wait
                    if voiture.time + temps < self.time_end:
                        voiture.log.append(("charge", voiture.time + temps, voiture.location))
                        voiture.t_charge += t_charge
                        self.route.etapes[voiture.location].t_use += t_charge
                    else:
                        voiture.log.append(("charge", self.time_end, voiture.location))
                        voiture.t_charge += self.time_end - voiture.time - t_wait
                        self.route.etapes[voiture.location].t_use += self.time_end - voiture.time - t_wait
                else:
                    if t_wait.total_seconds() > 0:
                        voiture.log.append(("wait", self.time_end, voiture.location))
                        self.route.etapes[voiture.location].t_wait += self.time_end - voiture.time
                    voiture.t_wait += self.time_end - voiture.time

        else:
            temps = voiture.get_time_to_next_charge(self.route)
            voiture.in_charge = True

            if temps != None and temps != -1:
                voiture.log.append(("avance", voiture.time + temps, voiture.location))
        return temps

    def get_voiture_plus_tot(self):
        if (len(self.etats.keys()) == 0):
            return None

        plus_tot = min(self.etats.keys())
        voiture_plus_tot = self.etats[plus_tot][0]
        self.etats[plus_tot].pop(0)
        if len(self.etats[plus_tot]) == 0:
            self.etats.pop(plus_tot)
        self.time = plus_tot
        return voiture_plus_tot

    def stat_time_par_voiture(self):
        # print("----- STAT : time par Voiture -----")
        t_wait = []
        t_charge = []
        t_global = []

        for voiture in self.voitures:
            t_wait.append(voiture.t_wait)
            t_charge.append(voiture.t_charge)
            t_global.append(voiture.time - voiture.time_start)

        return t_wait, t_charge, t_global

    # def stat_time_par_borne(self):
    #     # print("----- STAT : time par Borne -----")
    #     t_wait = []
    #     t_use = []
    #     n_pompe_par_borne = []
    #     t_global=self.time_end-self.time_start
    #
    #     for borne in self.bornes :
    #         t_wait.append(borne.t_wait)
    #         t_use.append(borne.t_use)
    #         n_pompe_par_borne.append(len(borne.pompes))
    #
    #     return t_wait, t_use, t_global, n_pompe_par_borne
    def stat_time_par_borne(self):
        # print("----- STAT : time par Borne -----")
        t_wait = []
        t_use = []
        t_global = self.time_end - self.time_start

        for borne in self.bornes:
            t_wait.append(borne.tab_wait)
            t_use.append(borne.tab_use)

        return t_wait, t_use, t_global
