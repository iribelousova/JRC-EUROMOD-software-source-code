"""
This script runs one simulation test, with default options, on the Simpleland country.
"""


import pandas as pd
import os
from euromod import Model

def test():
    print('\n\nPlease provide the full path to the EUROMOD model root folder:\n')
    PATH_EUROMODFILES = input()
    PATH_EUROMODFILES = PATH_EUROMODFILES[1:-1] if PATH_EUROMODFILES[0]=="'" or PATH_EUROMODFILES[0]== '"' else PATH_EUROMODFILES
    
        
    ID_DATASET = 'sl_demo_v4.txt'
    PATH_DATA = os.path.join(PATH_EUROMODFILES,'Input',ID_DATASET)
    COUNTRY = 'SL'
    ID_SYSTEM = 'SL_1996'
        
    # load model
    mod =Model(PATH_EUROMODFILES)
    
    # display available countries in euromod
    # mod.countries
    # mod[COUNTRY].name
    
    # load country
    mod[COUNTRY].load()
    # mod.countries[COUNTRY].load()
    
    print('\n',mod.countries[COUNTRY],': Simpleland')
    print('\nSystem  Data (best-match)  Currency')
    for sysobj in mod[COUNTRY].systems:
        print(sysobj.name, '', sysobj.bestMatchDatasets, '    ', sysobj.currencyParam)
    
    
    # data=mod[COUNTRY].load_data(ID_DATASET, PATH_DATA = PATH_DATA)
    data = pd.read_csv(PATH_DATA,sep="\t")
    
    print('\nTesting simulation with default options...')
    out=mod[COUNTRY][ID_SYSTEM].run(data,ID_DATASET)
    print('\noutput:')
    print(out.outputs[0])
    
    print('\nSimulation successful!')
    
    
    # print('Testing simulation run with constantsToOverwrite...')
    # out = mod[COUNTRY][ID_SYSTEM].run(data,ID_DATASET,constantsToOverwrite = {("$f_h_cpi","2022"):'10000'})
    
    
    # print('Testing simulation run with addons...')
    # out = mod[COUNTRY][ID_SYSTEM].run(data,ID_DATASET,addons = [("LMA","LMA_"+COUNTRY)])
    
    # print('Testing simulation run with switches...')
    # out = mod[COUNTRY][ID_SYSTEM].run(data,ID_DATASET,switches = [("BTA",True)])

if __name__ == "__test__":
   test()
