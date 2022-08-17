#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 10 17:29:02 2022

@author: gokturkdede
"""
from gurobipy import *
import pandas as pd
import numpy as np
yeni_arac = pd.read_csv('C:/Users/BK-FENS-3/Desktop/gokturk/yeni/yeni_arac_datasi.csv',encoding= 'unicode_escape')
Dmk = np.genfromtxt('C:/Users/BK-FENS-3/Desktop/gokturk/yeni/water-fire distances.csv', delimiter=',', names=True, case_sensitive=True)
Djm = np.genfromtxt('C:/Users/BK-FENS-3/Desktop/gokturk/yeni/yeni_base-water distances son hali.csv', delimiter=',', names=True, case_sensitive=True)
yeni_yangin = pd.read_csv('C:/Users/BK-FENS-3/Desktop/gokturk/yeni/yeni_yangin_datasi (1).csv',encoding= 'unicode_escape')
#display(yeni_arac)
Si=list(yeni_arac['Hýz'])
C=list(yeni_arac['Kapasite'])
I=len(yeni_arac['Arac'])
Rk=list(yeni_yangin['risk'])
Pk=list(yeni_yangin['probability'])


def Output(m):  
    # Print the result
    # status_code = {1:'LOADED', 2:'OPTIMAL', 3:'INFEASIBLE', 4:'INF_OR_UNBD', 5:'UNBOUNDED'} #this is how a 'dictionary' 
    #                                                                                         #is defined in Python
    # status = m.status
    
    # print('The optimization status is ' + status_code[status])
    # if status >= 1:    
        # Retrieve variables value
    print('Optimal solution:')
    for v in m.getVars():
        print(str(v.varName) + " = " + str(v.x))    
    print('Optimal objective value: ' + str(m.objVal) + "\n")


m=Model('inv')
 
m.setParam('OutputFlag',True)
m.setParam('TimeLimit', 6*60*60)
Fk=[150,130,150,112,135,390,210,100,100,100]

T=190# number of vehicle’s attack number
I=9 # number of vehicle
J=8  # number of base
M=37# number of water source
K=9  # number of possible fire front



y=m.addVars(I,J,vtype=GRB.BINARY,name=['y_'+str(i+1)+str(j+1) for i in range(I) for j in range(J)])

y1=m.addVars(I,M,vtype=GRB.BINARY,name=['y1_'+str(i+1)+str(m+1) for i in range(I) for m in range(M)])

y2=m.addVars(I,K,vtype=GRB.BINARY,name=['y2_'+str(i+1)+str(k+1) for i in range(I) for k in range(K)])

Tik=m.addVars(I,K,vtype=GRB.CONTINUOUS,lb=0,name=['Tik_'+str(i+1)+str(k+1) for i in range(I)  for k in range(K)])

Tikt=m.addVars(I,K,T,vtype=GRB.CONTINUOUS,lb=0,name=['Tik_'+str(i+1)+str(k+1)+str(t+1) for i in range(I)  for k in range(K) for t in range(T)])
   
Z=m.addVars(I,K,vtype=GRB.CONTINUOUS,lb=0,name=['Z_'+str(i+1)+str(k+1) for i in range(I) for k in range(K)])

W=m.addVars(I,K,T,vtype=GRB.BINARY,name=['W_'+str(i+1)+str(k+1)+str(t+1) for i in range(I) for k in range(K) for t in range(T)])

Dik=m.addVars(I,K,vtype=GRB.CONTINUOUS,lb=0,name=['Dik_'+str(i+1)+str(k+1) for i in range(I) for k in range(K)])

L=m.addVars(I,K,vtype=GRB.BINARY,name=['L_'+str(i+1)+str(k+1) for i in range(I) for k in range(K)])

Wimt=m.addVars(I,M,T,vtype=GRB.BINARY,name=['Wimt_'+str(i+1)+str(m+1)+str(t+1) for i in range(I) for m in range(M) for t in range(T)])

Tk=m.addVars(K,vtype=GRB.CONTINUOUS,lb=0,name=['Tk_'+str(k+1) for k in range(K)])

Tk2=m.addVars(K,vtype=GRB.CONTINUOUS,lb=0,name=['Tk2_'+str(k+1) for k in range(K)])


  
m.setObjective(quicksum(Tk2[k]*Pk[k] for k in range(0,K)), GRB.MINIMIZE)


m.addConstr(quicksum(Tk[k]*Rk[k] for k in range(0,K))<=30)

for i in range(I):
    m.addConstr(quicksum(y[i,j] for j in range(J))==1)
    
for i in range(I):
    m.addConstr(quicksum(y1[i,m] for m in range(M))==1)
     
for i in range(I):
    m.addConstr(quicksum(y2[i,k] for k in range(K))==1)
for k in range(K):
    m.addConstr(quicksum(y2[i,k] for i in range(I))>=1)
    
for k in range(K):
    m.addConstr(quicksum(L[i,k] for i in range(I))==1)
    
for i in range(I):
   for k in range(K):
       m.addConstr(Dik[i,k] ==(quicksum(Djm[j][m]*y[i,j]*y1[i,m] for j in range(J) for m in range(M)) + quicksum(Dmk[m][k]*y2[i,k]*y1[i,m] for k in range(K) for m in range(M)) ))
       m.addConstr(Dik[i,k]*y2[i,k]>=0)
       


for i in range(I):
    for k in range(K):
        m.addConstr(Tik[i,k] == 50000*(1-y2[i,k])+Dik[i,k]/Si[i])
        m.addConstr(Tik[i,k] >=0)
        
for i in range(I):
    for k in range(K):
        m.addConstr(Tk[k] <= Tik[i,k])
        m.addConstr(Tk[k] >= Tik[i,k]*L[i,k])
    
    
for i in range(I):
    for t in range(T):
        m.addConstr(quicksum(Wimt[i,m,t] for m in range(M))==1)
    
for t in range(T):
    m.addConstr(quicksum(W[i,k,t]for i in range(I) for k in range(K))==1)

for k in range(K):
    m.addConstr(quicksum(C[i]*Z[i,k] for i in range(I))>=Fk[k]- quicksum(y2[i,k]*C[i] for i in range(I)))
    
   
   
for k in range(K):
    for i in range(I):
        m.addConstr(quicksum(W[i,k,t] for t in range(T))==Z[i,k])
        
        
for i in range(I):
    for k in range(K):
        for t in range(T):
            m.addConstr(Tikt[i,k,t] == quicksum(2*Dmk[m][k]*Wimt[i,m,t] for m in range(M))/Si[i]*W[i,k,t])
            
            
        
for i in range(I):
    for k in range(K):
        m.addConstr(Tk2[k] >= Tk[k]+quicksum(Tikt[i,k,t]for t in range(T)))
        
        


m.optimize()

Output(m)
m.write('inv.lp')
m.write('inv.sol')
varlist=[y,y1,y2,Tik,Tikt,Tk,Tk2]
a=m.printAttr('x') 
count=0
for i in varlist:
    count=count+1
    valname=[]
    varvalue=[]
    for v in i.values():
        valname.append(v.varName)
        varvalue.append(v.X)
        
    data=[]
    data=pd.DataFrame(data)
    data['variable']=valname
    data['variable_value']=varvalue

    
    data.to_csv('C:/Users/BK-FENS-3/Desktop/gokturk/t_190/data'+str(count)+'.csv', index=False)






