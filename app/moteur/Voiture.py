import datetime


class Voiture:

    def __init__(self,autonomie,start,time_start,end,km_after_end,autonomie_max,capacite):
        self.nom= "Ferrari"
        self.autonomie_max=autonomie_max
        self.autonomie=autonomie
        self.location=start
        self.start=start
        self.time_start = time_start
        self.time=time_start
        self.end=end
        self.km_after_end=km_after_end
        self.dist_to_next_borne=0
        self.in_charge=False
        self.capacite=capacite

        self.vitesse=130

        self.log=[("start",self.time,self.location)]
        self.t_wait=datetime.timedelta()
        self.t_charge=datetime.timedelta()

    def get_time_to_wait_and_charge(self,borne,autonomie_desire,time_end):
        self.remove_voiture_chargee(borne)
        idx_pompe=borne.get_index_pompe()

        time_to_charge=self.get_time_to_charge(borne.pompes[idx_pompe],autonomie_desire)
        time_to_wait=datetime.timedelta()

        if borne.pompes[idx_pompe].get_len_fifo()>0 :
            time_to_wait=borne.pompes[idx_pompe].fifo[-1]-self.time

        heure_to_go=self.time+time_to_wait+ time_to_charge
        borne.pompes[idx_pompe].fifo.append(heure_to_go)

        borne.tab_wait[idx_pompe].append(self.min_date(time_to_wait,self.max_date(time_end-self.time,datetime.timedelta())))
        borne.tab_use[idx_pompe].append(self.min_date(time_to_charge,self.max_date(time_end-time_to_wait-self.time,datetime.timedelta())))

        return time_to_wait,time_to_charge

    def min_date(self,date1,date2):
        if date1.total_seconds()>date2.total_seconds():
            return date2
        else :
            return date1

    def max_date(self,date1,date2):
        if date1.total_seconds()<date2.total_seconds():
            return date2
        else :
            return date1


    def get_time_to_charge(self,pompe,autonmie_desire):
        heure=(autonmie_desire-self.autonomie)/pompe.puissance
        self.autonomie = autonmie_desire
        return datetime.timedelta(hours=heure)

    def remove_voiture_chargee(self,borne):
        for pompe in borne.pompes :
            while pompe.get_len_fifo()>0 and pompe.fifo[0]<self.time :
                pompe.fifo.pop(0)

    def get_time_to_next_charge(self,route):
        i=1
        bornes=self.get_bornes_utile(route)
        while (i<len(bornes)):
            if self.location+self.autonomie < bornes[i].location and self.location<bornes[i-1].location :
                self.dist_to_next_borne = self.get_dist_virtuelle_to_next_borne(bornes[i-1].location-self.location)
                self.autonomie-=self.dist_to_next_borne
                self.location+=self.dist_to_next_borne
                return self.get_time_to_avance(self.dist_to_next_borne)
            i+=1

        #Dernière station
        if self.location+self.autonomie < self.end and self.location<bornes[i-1].location :
            self.dist_to_next_borne = self.get_dist_virtuelle_to_next_borne(bornes[i-1].location - self.location)
            self.autonomie -= self.dist_to_next_borne
            self.location += self.dist_to_next_borne
            return self.get_time_to_avance(self.dist_to_next_borne)

        elif self.location+self.autonomie > self.end :
            #Avance jusqu'a la fin
            self.dist_to_next_borne = self.get_dist_virtuelle_to_next_borne(self.end - self.location)
            self.autonomie -= self.dist_to_next_borne
            self.location += self.dist_to_next_borne
            # self.time += self.get_time_to_avance(self.dist_to_next_borne)
            return self.get_time_to_avance(self.dist_to_next_borne)
        return None

    def get_time_to_avance(self,km):
        return datetime.timedelta(hours=km/self.vitesse)


    #Gérer l'autonomie avec la température, l'age de la batterie ...
    def get_dist_virtuelle_to_next_borne(self,dist_reel):
        return min(self.autonomie,dist_reel)


    def get_bornes_utile(self,route):
        bornes_utiles=[]
        bornes=route.get_bornes()
        for borne in bornes :
            if borne.location > self.end :
                return bornes_utiles
            if borne.location > self.start :
                bornes_utiles.append(borne)
        return bornes_utiles

    def get_dist_to_next_stop(self,route):
        securite = 10
        bornes=self.get_bornes_utile(route)
        i=0
        while i < len(bornes) and bornes[i].location + securite <= self.location + self.autonomie_max:
            i += 1

        if i == len(bornes):
            next_location=self.end+self.km_after_end+securite+securite
        else :
            next_location = bornes[i].location + securite

        return min(next_location-self.location,self.autonomie_max)

    def toString(self):
        for action,date,lieu in self.log :
            print("(",action,lieu,") -[",date,end=" ]-> ")
        print()

