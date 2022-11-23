# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 21:41:33 2022

@author: hp
"""

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

id_ = '010210059'

tre = 0.0005

def factor(id_): return sum([int(x) for x in id_])

def K(f,L,D): return (8*f*L)/(9.81*math.pi**2*D**5)

def head_lose(K,Q): return K*Q**2

def head_lose_Q(head_lose,Q): return head_lose/Q

def head_lose_sign(head_lose,direction): return head_lose*direction

def delta_Q(loop): return sum(loop['hf']*loop['direction'])/(2*(sum(loop['hf_Q'])))




e = (0.26/1000) * factor(id_)


data=pd.DataFrame(index=['ab','ad','bc','bg','gh','ch','de','ge','ef','hf'],
                  columns=['Q','L','D','e/D','f','K'])
data['Q'] = np.array([0.2, 0.1, 0.08, 0.12, 0.02, 0.03, 0.1, 0., 0.1, 0.05])
data['L'] = np.array([300., 250., 350., 125., 350., 125., 300., 125., 350., 125.])
data['D'] = np.array([0.3, 0.25, 0.2, 0.2, 0.2, 0.2, 0.2, 0.15, 0.2, 0.15])
data['f'] = np.array([0.019, 0.02, 0.021, 0.021, 0.021, 0.021, 0.021, 0.022, 0.021, 0.022])
data = data * factor(id_)

data['e/D'] = e/data['D']


for i in data.index:
    data.loc[i,'K'] = K(data.loc[i]['f'],data.loc[i]['L'],data.loc[i]['D'])



loop1 = pd.DataFrame(index=['ab','bg','ge','de','ad'],
                     columns=['direction', 'Q', 'K', 'hf', 'hf_Q', 'new_Q'])
loop2 = pd.DataFrame(index=['bc','bg','gh','ch'],
                     columns=['direction', 'Q', 'K', 'hf', 'hf_Q', 'new_Q'])
loop3 = pd.DataFrame(index=['gh','hf','ef','ge'],
                     columns=['direction', 'Q', 'K', 'hf', 'hf_Q', 'new_Q'])

loop1['direction'] = np.array([1, 1, -1, -1, -1])
loop2['direction'] = np.array([1, -1, -1, 1])
loop3['direction'] = np.array([1, 1, -1, 1])

loops = [loop1, loop2, loop3]

# =============================================================================
# loop1 = loop1.fillna(0)
# loop2 = loop2.fillna(0)
# loop3 = loop3.fillna(0)
# 
# =============================================================================


for i in loops:
    i['Q'] = np.array([x for x in data.loc[i.index]['Q']])
    i['K'] = np.array([K(data.loc[x]['f'],
                data.loc[x]['L'],
                data.loc[x]['D']) 
              for x in i.index])



convergance_Q = pd.DataFrame(index=data.index)

iter_num_ = [0,0,0]

is_on = [0, 0, 0]
delta_Q_ = np.array([1., 1., 1.])

iter_loop = 0
while is_on != [1, 1, 1]:
    
    
    for i in loops:
        
        convergance_Q.loc[i.index,iter_num_[iter_loop]] = i['Q']
        
        if is_on[iter_loop] == 0:
            
            for j in loops:
                j['Q'] = np.array([x for x in data.loc[j.index]['Q']])
        
            i['hf'] = np.array([head_lose(i.loc[x,'K'],
                                 data.loc[x,'Q'])
                                   for x in i.index])
            
            i['hf_Q'] = i['hf'] / i['Q']
            i['hf_Q'] = i['hf_Q'].fillna(0)
            

            delta_Q_[iter_loop] = delta_Q(i)
            
            if abs(delta_Q_[iter_loop]) >= tre:
                
                
# =============================================================================
#                 count += 1
# =============================================================================
                
                i['new_Q'] = i['Q'] + delta_Q_[iter_loop]*i['direction']*(-1)
                i['Q'] = i['new_Q']
                data.loc[i.index,'Q'] = i['Q']
                iter_num_[iter_loop] = iter_num_[iter_loop] + 1
                
               
                
            else:
                print(i, delta_Q_)
                i['iter'] = iter_num_[iter_loop]
                i['delta_q'] = delta_Q_[iter_loop]
                is_on[iter_loop] = 1
            
                
        if iter_loop == 2:
            iter_loop = 0
        else:
            iter_loop += 1



convergance_Q.T.plot.line()




