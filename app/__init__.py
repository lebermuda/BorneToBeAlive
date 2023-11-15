import json
import os
import sys
from os.path import join, dirname, realpath

sys.path.append("..")

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import app.moteur.Simulation as o_Simulation
import app.moteur.Resultat as o_Resultat

# from ..moteur.Simulation import *
# from ..moteur.Resultat import *

database = SQLAlchemy()

n_types = 3

# UPLOAD_FOLDER = '/uploaded'
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'uploaded/')


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        SQLALCHEMY_DATABASE_URI='sqlite:////' + os.path.abspath(os.getcwd()) + '/instance/btba.database'
        # SQLALCHEMY_DATABASE_URI='sqlite:////tmp/btba.database'
    )
    database.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # simu = Simulation("../moteur/init.json", "../moteur/scenario.json")

    from .models import Trajets, Voitures, Stations, Scenario

    @app.route('/', methods={'GET', 'POST'})
    def simulator():
        if 'scenario_id' in request.args:
            scenario = Scenario.query.filter_by(id=request.args["scenario_id"]).first()
        else:
            scenario = Scenario("", "A6", 0, 0, 0, 0, 0, 0, 0)

        scenarios = Scenario.query.all()
        trajets_configs = Trajets.query.all()
        voitures_configs = Voitures.query.all()
        stations_configs = Stations.query.all()

        return render_template('simulator.html', scenarios=scenarios, voitures_configs=voitures_configs,
                               trajets_configs=trajets_configs, stations_configs=stations_configs,
                               scenario=scenario)

    @app.route("/test")
    def test():
        return render_template('test.html')

    @app.route('/simulate', methods=['GET', 'POST'])
    def run_simulation():
        scenario = create_edit_scenario()

        path=None
        file = request.files.get('file_scenario')

        if file:
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)

        # Make Simu
        simul = o_Simulation.Simulation("app/static/scenarios/init.json", scenario, path)
        # simul.route.print_route(1)
        simul.run_simulation()
        # o_Resultat.print_log(simul)

        json_result = o_Resultat.get_json_resultat(simul)
        print(json_result)

        return json_result

    @app.route('/stations/<id>', methods=['GET', 'POST'])
    def stations(id):
        stations_obj = Stations.query.filter_by(id=id).first()
        if request.method == 'GET':
            return render_template('config_stations_view.html', stations=stations_obj)
        if request.method == 'POST':
            form = request.form
            stations_obj.name = form['name']
            stations_obj.stations = [{
                "id_station": str(i + 1),
                "station_typeA": form["station" + str(i + 1) + "_typeA"],
                "station_typeB": form["station" + str(i + 1) + "_typeB"],
                "emplacement": form["emplacement" + str(i + 1)]
            } for i in range(int(form["n_stations"]))]

            database.session.commit()
            return redirect('/')

    @app.route('/stations/new', methods=['GET', 'POST'])
    def new_stations():
        if request.method == 'GET':
            return render_template('config_stations_create.html')
        if request.method == 'POST':
            form = request.form
            new_stations_config = Stations(request.form['name'])
            new_stations_config.stations = [{
                "id_station": str(i + 1),
                "station_typeA": form["station" + str(i + 1) + "_typeA"],
                "station_typeB": form["station" + str(i + 1) + "_typeB"],
                "emplacement": form["emplacement" + str(i + 1)]
            } for i in range(int(form["n_stations"]))]
            database.session.add(new_stations_config)
            database.session.commit()

            return redirect('/')

    @app.route('/stations/delete/<id>')
    def delete_stations(id):
        stations = Stations.query.filter_by(id=id).first()
        database.session.delete(stations)
        database.session.commit()
        return redirect('/')

    @app.route('/voitures/<id>', methods=['GET', 'POST'])
    def voitures(id):
        voitures_config = Voitures.query.filter_by(id=id).first()
        if request.method == 'GET':
            return render_template('config_voitures_view.html', voitures=voitures_config)
        if request.method == 'POST':
            voitures_config.name = request.form['name']
            voitures_config.voitures = [request.form['type' + str(i)] for i in range(n_types)]
            voitures_config.voitures = [
                {"nom": "Tesla_Model_3_Performance", "autonomie_max": 547, "capacite": 76,
                 "proportion": request.form['type1']},
                {"nom": "Renault_Zoé_50_R110", "autonomie_max": 390, "capacite": 52,
                 "proportion": request.form['type2']},
                {"nom": "Renault_Zoé_40_Q90", "autonomie_max": 301, "capacite": 41,
                 "proportion": request.form['type3']}]
            database.session.commit()

            return redirect('/')

    @app.route('/voitures/new', methods=['GET', 'POST'])
    def new_voitures():
        if request.method == 'GET':
            return render_template('config_voitures_create.html')
        if request.method == 'POST':
            new_voitures_config = Voitures(request.form['name'])
            new_voitures_config.voitures = [request.form['type' + str(i)] for i in range(n_types)]
            database.session.add(new_voitures_config)
            database.session.commit()

            return redirect('/')

    @app.route('/voitures/delete/<id>')
    def delete_voitures(id):
        voitures = Voitures.query.filter_by(id=id).first()
        database.session.delete(voitures)
        database.session.commit()
        return redirect('/')

    @app.route('/trajets/<id>', methods=['GET', 'POST'])
    def trajets(id):
        trajets = Trajets.query.filter_by(id=id).first()
        if request.method == 'GET':
            return render_template('config_trajets_view.html', trajets=trajets)
        if request.method == 'POST':
            trajets.repartition_voiture = [int(x) for x in request.form['repartition_voiture_formated'].split(',')]
            trajets.type_trajet = [{"km_start": int(request.form["km_entree_" + str(i)]),
                                    "km_end": int(request.form["km_sortie_" + str(i)])}
                                   for i in range(int(request.form['n_trajets']))]
            trajets.proportion_trajet_par_heure = [
                [int(x) for x in request.form['distrib_trajet_' + str(i) + '_formated'].split(',')]
                for i in range(int(request.form['n_trajets']))
            ]
            database.session.commit()
            return redirect('/')

    @app.route('/trajets/new', methods=['GET', 'POST'])
    def new_trajets():
        if request.method == 'GET':
            return render_template('config_trajets_create.html')

        if request.method == 'POST':
            new_trajets = Trajets(request.form['name'])
            # new_trajets.type_journee = request.form['type_journee']
            new_trajets.repartition_voiture = [int(x) for x in request.form['repartition_voiture_formated'].split(',')]
            new_trajets.type_trajet = [{"km_start": int(request.form["km_entree_" + str(i)]),
                                        "km_end": int(request.form["km_sortie_" + str(i)])}
                                       for i in range(int(request.form['n_trajets']))]
            new_trajets.proportion_trajet_par_heure = [
                [int(x) for x in request.form['distrib_trajet_' + str(i) + '_formated'].split(',')]
                for i in range(int(request.form['n_trajets']))
            ]
            database.session.add(new_trajets)
            database.session.commit()
            return redirect('/')

    @app.route('/trajets/delete/<id>')
    def delete_trajets(id):
        trajets = Trajets.query.filter_by(id=id).first()
        database.session.delete(trajets)
        database.session.commit()
        return redirect('/')

    def create_edit_scenario():
        form = request.form
        scenario = Scenario.query.filter_by(name=form['scenario_name']).first()
        if scenario is None:
            scenario = Scenario(form['scenario_name'], "", 0, 0, 0, 0, 0, 0, 0)
            database.session.add(scenario)

        scenario.autoroute = form['autoroute']
        """scenario.stations = [{
            "id_station": str(i+1),
            "station_typeA": form["station" + str(i + 1) + "_typeA"],
            "station_typeB": form["station" + str(i + 1) + "_typeB"],
            "emplacement": form["emplacement" + str(i + 1)]
        } for i in range(int(form["n_stations"]))]"""
        # scenario.type_journee = form["type_journee"]
        scenario.h = form['h']
        scenario.min = form['min']

        if request.files['file_scenario'].filename == '':
            scenario.voitures_id = form['scenario_voitures']
            scenario.trajets_id = form['scenario_trajets']
            scenario.n_voitures = form['n_voitures']

        scenario.stations_id = form['scenario_stations']

        database.session.commit()

        return scenario

    @app.route('/scenario/save', methods={'POST'})
    def save_scenario():
        scenario = create_edit_scenario()
        return redirect(url_for('.simulator', scenario_id=scenario.id))

    @app.route('/scenario/get/<id>', methods={'GET'})
    def get_scenario(id):
        return Scenario.query.filter_by(id=id).first().serialize()

    @app.route('/stations/get/<id>', methods={'GET'})
    def get_stations(id):
        return Stations.query.filter_by(id=id).first().serialize()

    @app.route('/aires')
    def aires_info():
        import csv
        print(os.getcwd())
        with open(os.getcwd() + "/app/static/csv/aires-Paris-Lyon.csv", newline='') as csvfile:
            aires = list(csv.reader(csvfile, delimiter=';'))

        print(aires)
        return render_template("aires_info.html", aires=aires[1:])

    # from . import database
    database.init_app(app)

    with app.app_context():
        database.create_all()

    return app
