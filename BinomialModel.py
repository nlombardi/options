import pandas as pd
from pylab import *
import scipy.optimize
import numpy as np
from datetime import date
import time
import argparse


class Binomial:
    # 1-month CAD T-Bill yield Nov 18, 2019: 1.768%
    # S&P 500 Div Yield Nov 18, 2019: 1.83%
    def __init__(self, pdata, strike, volat, expiry, side='c', optStyle='a', rf=0.01768, dy=0.0183, call=100, put=101, euro=102, amer=103):
        self.pdata, self.strike, self.volat, self.expiry = pdata, strike, volat, expiry
        self.rf, self.dy, self.call, self.put, self.euro, self.amer = rf, dy, call, put, euro, amer
        self.levels = [None, None, None]
        self.u, self.d, self.pu, self.pd = 0, 0, 0, 0
        self.gamma, self.theta, self.delta, self.delta1, self.delta2, self.optionValue = 0, 0, 0, 0, 0, 0
        if side =='c':
            self.side = call
        elif side =='p':
            self.side = put
        if optStyle =='a':
            self.optStyle = amer
        elif optStyle =='e':
            self.optStyle = euro

    def __main__(self, n):
        side, OptType = self.call, self.amer
        self.tte = (date.fromisoformat(self.expiry) - date.today()).days
        self.tdelta = self.tte / (n * 365)
        self.price = self.pdata[-1]

        print('Calculation Inputs')
        print('%18s:%0.3f' % ('Price', self.price))
        print('%18s:%0.3f' % ('Strike', self.strike))
        print('%18s:%0.3f' % ('Risk-free', self.rf))
        print('%18s:%0.3f' % ('Div Yield', self.dy))
        print('%18s:%0.3f' % ('TTE Days', self.tte))
        print('%18s:%0.3f' % ('Volatility', self.volat))

    def ProcessInputs(self, volat):
        ''' n- # of steps, tte- time to expiration, volat- annual volatility'''
        self.u = exp(volat*self.tdelta**0.5)  # Up movement per step
        self.d = 1 / self.u  # Down movement per step
        print("U - %s, D - %s" % (self.u,self.d))
        self.rf = exp(self.rf * self.tdelta) - 1  # Risk Free rate per step
        self.dy = exp(self.dy * self.tdelta) - 1  # Divided yield per step
        self.pu = (1 + self.rf - self.dy - self.d) / (self.u - self.d)  # Probability of an up movement
        self.pd = 1 - self.pu  # Probability of a downstep

        assert self.side in [self.call, self.put] and self.optStyle in [self.amer, self.euro]
        print('%18s:%0.3f' % ('Node Prob U', self.pu))
        print('%18s:%0.3f' % ('Node Prob D', self.pd))
        print('%18s:%0.3f' % ('Node tdelta', self.tdelta))
        print('%18s:%0.3f' % ('Node discount f', self.rf))
        print("")

    def tree(self, n):
        ''' n - # of steps '''
        # Generate terminal nodes of binomial tree
        print("Binomial Tree")
        print("")
        level = []
        for i in range (0, n+1): # iterates through nodes from highest to lowest
            # price at node i
            pr = self.price*self.d**i*self.u**(n-i)
            # option value at the node (depending on the side [call,put])
            ov = max(0.0, pr-self.strike) if self.side==self.call else max(0.0, self.strike-pr)
            level.append((pr,ov))
            print('Node [%i, %i] \t Price %6.3f \t Option Value %6.3f' % (n, i, pr, ov))

        # reduce the binomial tree
        for j in range(n-1, -1, -1): # [n-1 to 0]
            levelNext = []
            print()
            for k in range(0, j+1): # iterate through the nodes from highest to lowest
                node_u, node_d = level[k], level[k+1]
                # instrument price at the node
                pr = node_d[0]/self.d
                # Option value at the node (depending on side)
                ov = (node_d[1]*self.pd+node_u[1]*self.pu)
                if self.optStyle == self.amer: # American option can be excercised at any time
                    ov = max(ov, pr-self.strike if self.side == self.call else self.strike - pr)
                levelNext.append((pr,ov))
                print('Node [%i, %i] \t Price %6.3f \t Option Value %6.3f' % (j, k, pr, ov))
            level = levelNext
            if k <= 2: self.levels[k] = level # save level 0,1,2 of the tree

    def greeks(self):
        optionValue = self.levels[0][0][1]
        self.delta = (self.levels[1][0][1] - self.levels[1][1][1]) / (self.levels[1][0][0] - self.levels[1][1][0])
        self.delta1 = (self.levels[2][0][1] - self.levels[2][1][1]) / (self.levels[2][0][0] - self.levels[2][1][0])
        self.delta2 = (self.levels[2][1][1] - self.levels[2][2][1]) / (self.levels[2][1][0] - self.levels[2][2][0])
        self.gamma = (self.delta1 - self.delta2) / (self.levels[2][0][0] - self.levels[2][2][0])
        theta = (self.levels[2][1][1] - self.optionValue) / (2 * self.tdelta)
        print(f"Option Value: {self.optionValue} "
              f"\nDelta: {self.delta} \t Delta 1: {self.delta1} \t Delta 2: {self.delta2}"
              f"\nGamme: {self.gamma} \t Theta: {self.theta}")


def parsedate(date):
    try:
        return time.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(date + 'is not a proper date format')


path = 'C:/Users/nick/Documents/Development/Python/Options Pricing Models/Binomial Model/'
df = pd.read_csv(path + 'iSharesIndex.csv', index_col=None, parse_dates=['date'])
prices = np.array(df['close'])[-250:]  # 6-months of trading days

plot(prices), xlabel('time'), ylabel('prices')
show()

returns = log(prices[1:] / prices[:-1])  # calc of daily continuous asset returns r=log(p1-pt-1)
vDaily = np.std(returns)  # Daily volatility
v = sqrt(vDaily**2*250)  # Annualized volatility
    # TODO: look into reverse valuation process to imply the volatility from other options'

Binomial = Binomial(pdata=prices, strike=101, volat=v, expiry='2020-12-21')
Binomial.__main__(n=3)
Binomial.ProcessInputs(volat=v)
Binomial.tree(n=3)
Binomial.greeks()