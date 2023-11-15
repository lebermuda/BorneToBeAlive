import app.moteur.Etape as Etape


class Sortie(Etape.Etape):

    def __init__(self,nom,km,numero):
        self.nom=nom
        self.location=km
        self.numero=numero