import datetime

import app.moteur.Simulation as o_Simulation


# MODELE DE FONCTION
# def get_caracteristique(simul,other_args,verbose=False):
#     t_wait, t_charge, t_global = simul.stat_time_par_voiture()
#     # OR
#     t_wait, t_charge, t_global, n_pompe = simul.stat_time_par_borne()
#
#     # COMPUTE caractéristique
#
#     if verbose :
#         print("caractéristique")

def get_resultats_globaux_voiture(simul, verbose=False):
    # return resultat pour les voitures
    #   temps d'attente moyen
    #   temps de charge moyen
    #   proportion de (temps de roule / temps de voyage) moyenne

    t_wait, t_charge, t_global = simul.stat_time_par_voiture()


    # COMPUTE caractéristique
    temps_attente = datetime.timedelta()
    temps_charge = datetime.timedelta()
    n_charge=0
    pourcentage_roule = []

    for i in range(len(t_wait)):
        if t_charge[i].total_seconds() > 0:
            temps_charge += t_charge[i]
            temps_attente += t_wait[i]
            n_charge+=1
        if (t_global[i].total_seconds() > 0) :
            pourcentage_roule.append((t_global[i].total_seconds() - t_wait[i].total_seconds() - t_charge[i].total_seconds()) / t_global[i].total_seconds())
        # else :
        #     pourcentage_roule.append(None)

    t_wait_m = str(temps_attente / n_charge) if n_charge>0 else "None"
    t_charge_m = str(temps_charge / n_charge) if n_charge>0 else "None"
    taux_use_m = "{0:.3f}".format(sum(pourcentage_roule) / len(pourcentage_roule)) if len(pourcentage_roule)>0 else None

    if verbose:
        print("Temps d'attente moyen : ", temps_attente / n_charge)
        print("Temps de charge moyen : ", temps_charge / n_charge)
        print("Pourcentage roule: ", end="")
        for p in pourcentage_roule:
            print("{0:.3f}".format(p), end=" | ")
        print("=> ", taux_use_m, "\n")

    # print("n_charge => ",n_charge)

    return t_wait_m,t_charge_m,taux_use_m


def get_pourcentage_arret(simul, verbose=False):
    pourcentage_arret = []
    t_wait, t_charge, t_global = simul.stat_time_par_voiture()

    for i in range(len(t_wait)):
        pourcentage_arret.append(
            (t_wait[i].total_seconds() + t_charge[i].total_seconds()) / t_global[i].total_seconds())

    if verbose:
        print("Pourcentage à l'arrêt :")
        for p in pourcentage_arret:
            print(p, end=" | ")
        print()

    return pourcentage_arret


def get_resultats_globaux_par_borne(simul, verbose=False):
    t_wait, t_use, t_global = simul.stat_time_par_borne()
    taux_wait = []
    taux_use = []

    compteur=0


    t_use_mean = []
    t_wait_mean = []

    for i in range(len(t_wait)):
        t_wait_mean.append(0)
        t_use_mean.append(0)

        taux_wait.append(datetime.timedelta())
        taux_use.append(datetime.timedelta())
        for j in range(len(t_wait[i])):
            # print(len(t_wait[i][j]))

            for k in range(len(t_wait[i][j])):
                compteur+=1
                t_wait_mean[-1] += 1
                t_use_mean[-1] += 1

                taux_wait[-1] += t_wait[i][j][k]
                taux_use[-1] += t_use[i][j][k]

        if t_wait_mean[-1] != 0:
            t_wait_mean[-1] = str(taux_wait[-1] / t_wait_mean[-1])
        if t_use_mean[-1] != 0:
            t_use_mean[-1] = str(taux_use[-1] / t_use_mean[-1])

        taux_wait[-1] = "{0:.3f}".format(taux_wait[-1]/(t_global * len(t_wait[i])))
        taux_use[-1] = "{0:.3f}".format(taux_use[-1]/(t_global * len(t_wait[i])))
    # print("compteur => ",compteur)



    if verbose:
        print("Temps d'attente moyen par station : ", end="")
        for t in t_wait_mean:
            print(t, end=" | ")
        print("\nTemps d'utilisation moyen par station : ", end="")
        for t in t_use_mean:
            print(t, end=" | ")
        print("\nTaux d'attente par station : ", end="")
        for t in taux_wait:
            print(t, end=" | ")
        print("\nTaux d'utilisation par station : ", end="")
        for t in taux_use:
            print(t, end=" | ")
        print()

    return taux_wait, taux_use, t_wait_mean, t_use_mean


def get_graph_repartition(simul, station, verbose=False):
    # Avoir la répartition des temps d'attente pour le graphe
    # définir le pas et le nombre de colonne
    pas = 10
    colonne = 13
    t_wait, t_use, t_global = simul.stat_time_par_borne()
    repartition = [0] * colonne

    for j in range(len(t_wait[station])):
        for t in t_wait[station][j]:
            for step in range(colonne - 1):
                if datetime.timedelta(minutes=step * pas) <= t < datetime.timedelta(minutes=(step + 1) * pas):
                    repartition[step] += 1
            if datetime.timedelta(minutes=(colonne - 1) * pas) <= t:
                repartition[-1] += 1

    if verbose:
        print("Repartition de l'attente pour la station ", station, " : ", end="")
        for data in repartition:
            print(data, end=" | ")
        print()

    return repartition


def print_log(simul):
    print("----- LOGS : etapes par voiture -----")
    for voiture in simul.voitures:
        voiture.toString()


def print_borne_res(simul, borne):
    t_wait, t_use, t_global = simul.stat_time_par_borne()
    print("BORNE ", borne)
    print("t_wait : ", end="")
    for t in t_wait[borne]:
        print(t, end=" ")
    print("\nt_use : ", end="")
    for t in t_use[borne]:
        print(t, end=" ")
    print("\nt_global : ", t_global)


def get_json_resultat(simul):
    t_wait_mean_v, t_use_mean_v, proportion_route_mean_v = get_resultats_globaux_voiture(simul)
    _, proportion_route_mean_b, t_wait_mean_b, _ = get_resultats_globaux_par_borne(simul)
    repartitions = []
    for i in range(len(simul.bornes)):
        repartitions.append(get_graph_repartition(simul,i))

    json_res = {
        "t_wait_mean_v": t_wait_mean_v,
        "t_use_mean_v": t_use_mean_v,
        "proportion_route_mean_v": proportion_route_mean_v,
        "t_wait_mean_b": t_wait_mean_b,
        "proportion_usage_b": proportion_route_mean_b,
        "repartitions": repartitions
    }

    return json_res



