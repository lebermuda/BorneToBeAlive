import datetime

import app.moteur.Etape as Etape
import app.moteur.Pompe as Pompe

class Borne(Etape.Etape):

    def __init__(self,km,puissances):
        self.location=km
        self.pompes=[]

        self.tab_use=[]
        self.tab_wait=[]

        for puissance in puissances :
            self.pompes.append(Pompe.Pompe(puissance))
            self.tab_use.append([])
            self.tab_wait.append([])

        self.t_use=datetime.timedelta()
        self.t_wait=datetime.timedelta()



    def get_index_pompe(self):
        ind_min=0
        for i in range(len(self.pompes)):
            if self.pompes[ind_min].get_len_fifo() > self.pompes[i].get_len_fifo():
                ind_min=i

        return ind_min
