
# written by cwa 22/2/2024

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from vis import SimpleStatView
import pygame
import math

class Position():

    def __init__(self, entry, exit):
        self.entry = entry
        self.exit = exit

class Account():

    def __init__(self):
        self.balance = 50000
        self.pl = 0 # all time profit and loss
        self.daily_pl = 0 # daily profit and loss
        self.open_pl = 0 # current profit and loss of open trade
        self.positionquantity = 0
        self.position = Position(None, None)


class simulation_state():

    def __init__(self, startpoint, endpoint, increment): # change increment to speed (endpoint default as last record book-end)
        self.all = np.array([])
        self.price = -1
        self.lastprice = -1
        self.volume = 0
        self.day_high = -1
        self.day_low = 99999999
        self.va_high = -1
        self.va_low = 99999999
        self.day_low_hit = False
        self.day_high_hit = False
        self.vwap = -1
        self.date = datetime.strptime(startpoint, '%Y-%m-%d %H:%M:%S').date()
        self.ma7vals = np.zeros(7)
        self.ma7index = 0
        self.ma7 = -1
        self.ma17vals = np.zeros(17)
        self.ma17index = 0
        self.ma17 = -1
        self.ma41vals = np.zeros(41)
        self.ma41index = 0
        self.ma41 = -1


class simulation():
    
    def __init__(self, startpoint, endpoint, increment, filename=None):
        self.data = pd.read_pickle(filename + '.pkl')
        self.index = self.data[self.data['DateTime'] == startpoint].index[0] # get the index from the startpoint (makes it efficient to run simulator by just traversing indices)
        self.state = simulation_state(startpoint, endpoint, increment)
        self.visualizer = SimpleStatView()
        self.account = Account()    
        
    def buy(self):
        if self.account.positionquantity == 0:
            self.account.positionquantity += 1
            self.account.position.entry = self.state.price
            self.account.position.exit = self.state.price
        elif self.account.positionquantity == -1:
            self.account.positionquantity += 1
            self.account.balance += self.account.open_pl
            self.account.pl += self.account.open_pl
            self.account.daily_pl += self.account.open_pl
            self.account.open_pl = 0
            self.account.position.entry = None
            self.account.position.exit = None
        else:
            print('position quantity out of whack when flattening short position')
            exit

    def sell(self):
        if self.account.positionquantity == 0:
            self.account.positionquantity -= 1
            self.account.position.entry = self.state.price
            self.account.position.exit = self.state.price
        elif self.account.positionquantity == 1:
            self.account.positionquantity -= 1
            self.account.balance += self.account.open_pl
            self.account.pl += self.account.open_pl
            self.account.daily_pl += self.account.open_pl
            self.account.open_pl = 0
            self.account.position.entry = None
            self.account.position.exit = None
        else:
            print('position quantity out of whack when flattening long position')
            exit
        
    def update_state(self):
        
        currentdate = self.data['DateTime'].iloc[self.index].date()
        if currentdate != self.state.date:
            self.state.all = np.array([])
            self.state.price = -1
            self.state.lastprice = -1
            self.state.volume = 0
            self.state.day_high = -1
            self.state.day_low = 99999999
            self.state.va_high = -1
            self.state.va_low = 99999999
            self.state.day_low_hit = False
            self.state.day_high_hit = False
            self.state.vwap = -1
            self.state.date = currentdate
            self.state.ma7vals = np.zeros(7)
            self.state.ma7index = 0
            self.state.ma7 = -1
            self.state.ma17vals = np.zeros(17)
            self.state.ma17index = 0
            self.state.ma17 = -1
            self.state.ma41vals = np.zeros(41)
            self.state.ma41index = 0
            self.state.ma41 = -1

        # update prices
        if not math.isnan(self.data['close'].iloc[self.index]):
            self.state.lastprice = self.state.price
            self.state.price = self.data['close'].iloc[self.index]
        else:
            self.state.price = self.state.lastprice
        
        # update position
        if self.account.positionquantity != 0:
            self.account.position.exit = self.state.price
            if self.account.positionquantity == 1:
                self.account.open_pl = (((self.account.position.exit - self.account.position.entry) / 100) * 4) * 5
            elif self.account.positionquantity == -1:
                self.account.open_pl = (((self.account.position.entry - self.account.position.exit) / 100) * 4) * 5

        # update moving averages
        self.state.ma7vals[self.state.ma7index] = self.state.price
        self.state.ma7index = (self.state.ma7index + 1) % 7
        self.state.ma7 = sum(self.state.ma7vals) / 7

        self.state.ma17vals[self.state.ma17index] = self.state.price
        self.state.ma17index = (self.state.ma17index + 1) % 17
        self.state.ma17 = sum(self.state.ma17vals) / 17

        self.state.ma41vals[self.state.ma41index] = self.state.price
        self.state.ma41index = (self.state.ma41index + 1) % 41
        self.state.ma41 = sum(self.state.ma41vals) / 41

        # update volume and vwap
        new_vol = self.data['Volume'].iloc[self.index]
        if new_vol > 0:
            self.state.volume += new_vol
            weight = new_vol / float(self.state.volume)
            self.state.vwap = self.state.vwap * (1 - weight) + self.state.price * weight
        
        # update value areas
        for i in range(new_vol):
            self.state.all = np.append(self.state.all, self.state.price)
        sort_all = np.sort(self.state.all)
        if sort_all.size > 0:
            self.state.va_high = np.percentile(sort_all, 15)
            self.state.va_low = np.percentile(sort_all, 85)

        # reset line hit flags to false
        self.state.day_low_hit = False
        self.state.day_high_hit = False
        
        # update dayhigh and daylow
        if self.state.price > self.state.day_high:
            self.state.day_high = self.state.price
        if self.state.price < self.state.day_low:
            self.state.day_low = self.state.price
        if self.state.price == self.state.day_high:
            self.state.day_high_hit = True
        if self.state.price == self.state.day_low:
            self.state.day_low_hit = True
        
        self.visualizer.draw(self.state, self.account, self.data, self.index)

    def run(self):
        running = True
        while running:
            self.update_state()
            self.index = self.index + 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mousepos = pygame.mouse.get_pos()
                    if self.visualizer.button_click(10, 70, 50, 20, mousepos):
                        self.buy()  
                    elif self.visualizer.button_click(70, 70, 50, 20, mousepos):
                        self.sell()  

            self.visualizer.clock.tick(10)

        self.visualizer.quit()


###
                
# run simulator

sim = simulation(startpoint='2024-02-08 18:51:00', endpoint='2024-02-22 18:31:06', increment=1, filename='NQH41S')
sim.run()