from . import database


# TODO: ajouter tous les paramètres aux classes
class Trajets(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), unique=True, nullable=True)
    #type_journee = database.Column(database.Integer, nullable=False)
    repartition_voiture = database.Column(database.JSON, nullable=True)
    type_trajet = database.Column(database.JSON, nullable=True)
    proportion_trajet_par_heure = database.Column(database.JSON, nullable=True)

    scenarios = database.relationship('Scenario', backref='trajets', lazy=True)

    # other args

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Trajets %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "scenario": [s.serialize() for s in self.scenarios]
        }


class Voitures(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), unique=True, nullable=True)
    voitures = database.Column(database.JSON, nullable=True)

    scenarios = database.relationship('Scenario', backref='voitures', lazy=True)

    # other args

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Voitures %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "voitures": self.voitures,
            "scenario": [s.serialize() for s in self.scenarios]
        }


class Stations(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), unique=True, nullable=True)
    stations = database.Column(database.JSON, nullable=True)
    scenarios = database.relationship('Scenario', backref='scenario_stations', lazy=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Stations %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "stations": self.stations
        }


class Scenario(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), unique=True, nullable=True)
    autoroute = database.Column(database.String(20), nullable=False)
    # stations = database.Column(database.JSON, nullable=True)
    h = database.Column(database.Float, nullable=False)
    min = database.Column(database.Float, nullable=False)
    n_voitures = database.Column(database.Integer, nullable=False)

    voitures_id = database.Column(database.Integer, database.ForeignKey('voitures.id'))
    trajets_id = database.Column(database.Integer, database.ForeignKey('trajets.id'))
    stations_id = database.Column(database.Integer, database.ForeignKey('stations.id'))

    @property
    def stations(self):
        return Stations.query.filter_by(id=self.stations_id).first().stations

    @property
    def trajets(self):
        return Trajets.query.filter_by(id=self.trajets_id).first()

    @property
    def voitures(self):
        return Voitures.query.filter_by(id=self.voitures_id).first().voitures

    # other args

    def __init__(self, name, autoroute, type_journee, h, min, n_voitures, voitures_id,
                 trajets_id, stations_id):
        self.name = name
        self.autoroute = autoroute
        self.type_journee = type_journee
        self.h = h
        self.min = min
        self.n_voitures = n_voitures
        self.voitures_id = voitures_id
        self.trajets_id = trajets_id
        self.stations_id = stations_id

    def __repr__(self):
        return '<Scenario %r>' % self.name

# not up to date
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "voitures_id": self.voitures_id,
            "trajets_id": self.trajets_id,
            "stations": self.stations
        }

    def n_stations(self):
        return len(self.stations)

    def get_type_journee(self):
        if self.type_journee == 0:
            return "Milieu de semaine"
        elif self.type_journee == 1:
            return "Week-end"
        else:
            return "Vacances"

    def get_trajets(self):
         return Trajets.query.filter_by(id=self.trajets_id).first()

    def get_voitures(self):
        return Voitures.query.filter_by(id=self.voitures_id).first()

    def get_stations(self):
        return Stations.query.filter_by(id=self.stations_id).first()
