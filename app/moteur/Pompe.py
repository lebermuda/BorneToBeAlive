import datetime


class Pompe:

    def __init__(self,puissance):
        self.puissance=puissance
        self.fifo=[]

    def get_len_fifo(self):
        return len(self.fifo)
