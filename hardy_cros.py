# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 21:41:33 2022
@author: hp
"""

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

id_ = '1'

tre = 0.005

def factor(id_): return sum([int(x) for x in id_])

def K(f,L,D): return (8*f*L)/(9.81*math.pi**2*D**5)

def head_lose(K,Q): return K*Q**2

def head_lose_Q(head_lose,Q): return head_lose/Q

def head_lose_sign(head_lose,direction): return head_lose*direction

def delta_Q(loop): return round(sum(loop['hf']*loop['direction'])/(2*(sum(loop['hf_Q']))),3)



e = (0.26/1000) * factor(id_)


data=pd.DataFrame(index=['ab','ad','bc','bg','gh','ch','de','ge','ef','hf'],
                  columns=['Q','L','D','e/D','f','K'])
# =============================================================================
# data['Q'] = np.array([0.150,0.150,0.80,0.120,0.195,0.30,0.150,0.75,0.75,0.225])
# =============================================================================
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

loop1['direction'] = np.array([1, 1, 1, -1, -1])
loop2['direction'] = np.array([1, -1, -1, 1])
loop3['direction'] = np.array([1, 1, -1, -1])

loops = [loop1, loop2, loop3]

for i in loops:
    i['Q'] = np.array([x for x in data.loc[i.index]['Q']])
    i['K'] = np.array([K(data.loc[x]['f'],
                data.loc[x]['L'],
                data.loc[x]['D']) 
              for x in i.index])

writer = pd.ExcelWriter('hydrolics.xlsx')
convergance_Q = pd.DataFrame(index=data.index)
convergance_Q['initial'] = data['Q']

iter_num_ = [0,0,0]
is_on = [0, 0, 0]
delta_Q_ = np.array([1., 1., 1.])
iter_loop = 0

while is_on != [1, 1, 1]:
    for i, v in enumerate(loops):
        v['Q'] = np.array([x for x in data.loc[v.index]['Q']])
        v['hf'] = np.array([head_lose(v.loc[x,'K'],
                             data.loc[x,'Q'])
                               for x in v.index])
        v['hf_Q'] = v['hf'] / v['Q']
        v['hf_Q'] = v['hf_Q'].fillna(0)
        delta_Q_[i] = delta_Q(v)
        v['new_Q'] = v['Q'] + round(delta_Q_[i]*v['direction']*(-1),3)
        
        for k in v.index:
            if v.loc[k,'new_Q'] < 0:
                for m in loops:
                    for n in m.index:
                        if n == k:
                            v.loc[k, 'new_Q'] = abs(v.loc[k, 'new_Q'])
                            v.loc[k, 'direction'] *= -1
                            m.loc[k,'direction'] *=-1
        
        v['iter'] = iter_num_[i]
        v['delta_q'] = delta_Q_[i]
        
        v.to_excel(writer, sheet_name=f'Loop{i}-iteration{iter_num_[i]}', engine='xlsxwriter')
        
        v['Q'] = v['new_Q']
        data.loc[v.index,'Q'] = v['Q']
        iter_num_[i] = iter_num_[i] + 1
        convergance_Q.loc[v.index, iter_num_[i]] = v['Q']
       
        if abs(delta_Q_[i]) < tre: is_on[i] = 1

writer.save()
writer.close()