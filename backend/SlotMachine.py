from random import randint
import pandas as pd
from bresenham import bresenham as b
import itertools as it
import json

class SlotMachine(object):
    reels = []
    pos = []
    window = 0
    center_only = True
    display = []
    def __init__(self,num_reels=3,reel_array=[1,2,3,4,5,6,7,8,9,10],award_dict={1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,10:10},window=3,center_only=True):
        self.reels = pd.DataFrame([reel_array for i in range(num_reels)]).T
        print(self.reels)
        self.award_dict = award_dict
        self.window = window
        self.center_only = center_only
        self.spin()

    def spin (self):
        self.pos = pd.Series([randint(0,self.reels.shape[0]-1) for i in range(self.reels.shape[1])])
        self.display = self.getFinalWindow()

    def getReelPos(self):
        return self.pos.tolist()

    def getFinalWindow(self):
        l = self.reels.shape[0]
        p = self.pos.apply(lambda f: [(f+w)%l for w in range(self.window)])
        r = self.reels.apply(lambda f: f[p[f.name]].tolist())
        return r

    def visualize(self):
        print(self.display)
        print(self.reels)
        print(self.getMatches())

    def windowToJson(self):
        #return json.dumps({1:"Hello"})
        return self.display.to_json()

    def matchesToJson(self):
        m = self.getMatches()
        m = m[m[0]==True][[1,2]]
        #return json.dumps({1:"Hello"})
        return m.to_json(orient='records')

    def isMatch(self,row):
        m = row.apply(lambda f: f==row[0]).all()
        return pd.Series([m,row[0]])

    def getMatches(self):
        if self.center_only:
            c = int(round(self.window / 2, 0) - 1)
            cl = list(b(c, 0, c, self.display.shape[1]))
            return [self.isMatch(self.display.iloc[c]),cl]
        else:
            c = self.display.T.apply(lambda f: list(b(f.name,0,f.name,self.display.shape[1]-1)))
            cl = self.display.T.apply(lambda f: self.isMatch(f)).T
            print("***")
            cl[2] = c.values.tolist()
            print(cl)
            d1 = list(b(0,0,self.window-1,self.display.shape[1]-1))
            d1l = self.isMatch(pd.Series(d1).apply(lambda f: self.display.iloc[f[0],f[1]]))
            d1l[2] = d1
            d2 = list(b(0,self.display.shape[1]-1,self.window-1,0))
            d2l = self.isMatch(pd.Series(d2).apply(lambda f: self.display.iloc[f[0],f[1]]))
            d2l[2] = d2
            dl = pd.concat([d1l,d2l],axis=1).T
            df = pd.concat([cl, dl])
            return df

#    def getMatches(self):
#        if self.center_only:
#            c = int(round(self.window/2,0)-1)
#            return self.isMatch(self.display.iloc[c])
#        else:
#            c = self.display.apply(self.isMatch,axis=1)
#            d1 = self.isMatch(pd.Series(list(b(0,0,self.window-1,self.window-1))).apply(lambda f: self.display.iloc[f[0],f[1]]))
#            d2 = self.isMatch(pd.Series(list(b(0,self.window-1,self.window-1,0))).apply(lambda f: self.display.iloc[f[0],f[1]]))
#            return pd.DataFrame(c.tolist()+[d1]+[d2])

    def dispense (self):
        matches = self.getMatches()
        return int(matches[matches[0]==True][1].apply(lambda f: self.award_dict[f]).sum())

    def getReel(self):
        return self.reels[0].tolist()