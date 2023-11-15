import datetime

import moteur.Simulation as Simulation
import moteur.Resultat as Resultat

import app.moteur.Scenario as Scenario

def main():

    # # Test de charge avec n = 200000
    # simul=Simulation.Simulation("moteur/init.json","scenario/scenario_test.json")
    #
    # simul.route.print_route(5)
    #
    # t1 = datetime.datetime.now().timestamp()
    # simul.run_simulation()
    # t2=datetime.datetime.now().timestamp()
    #
    # print(t2-t1," secondes")

    # # Resultat.get_pourcentage_arret(simul,True)
    # Resultat.print_log(simul)
    # #Resultat.print_borne_res(simul)
    # Resultat.get_taux_utilisation_par_borne(simul,True)

    scenario1 = Scenario.Scenario()
    scenario1.create_scenario_json("scenario/carac_scenario_jour_semaine.json")

main()