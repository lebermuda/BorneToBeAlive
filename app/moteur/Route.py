import app.moteur.Sortie as Sortie
import app.moteur.Borne as Borne


class Route:

    def __init__(self,nom,km):
        self.nom=nom
        self.km=km
        self.etapes=dict()

    def add_etape(self,etape):
        self.etapes[etape.location]=etape
        self.etapes=dict(sorted(self.etapes.items()))

    def get_bornes(self):
        res=[]
        for loc,sortie in self.etapes.items():
            if (isinstance(sortie, Borne.Borne)):
                res.append(sortie)
        return res

    def print_route(self,echelle):
        print("|", end='')

        for km in range (0,self.km,echelle):
            i=km
            carac='='
            while (i<km+echelle):
                if i in self.etapes.keys():
                    if (isinstance(self.etapes[i], Borne.Borne)):
                        carac='b'
                        break
                    elif (isinstance(self.etapes[i], Sortie.Sortie)):
                        carac='s'
                i+=1
            print(carac, end='')
        print(">")
