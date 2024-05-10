import os
import pandas as pd
from pathlib import Path
import sys

"""
test_type : 1 for pre-build testing, i.e. the package is loaded from the local folder src/euromod
            2 for post-build testing, i.e. the package is loaded from the built package (location: C:\\Users\\XXX\\AppData\\Roaming\\Python\\PythonXXX\\site-packages\\euromod)
"""
test_type = 1 




###############################################################################
###############################################################################
curdir = Path(os.getcwd())
pkgdir = os.path.join(curdir.parent.absolute(), 'src') 

if test_type == 1:
    sys.path.insert(0, pkgdir)
    print('Testing local package ../src/euromod...')
elif test_type == 2:
    print('Testing installed package ../site-packages/euromod...')
    try:
        sys.path.remove(pkgdir)
    except:
        pass
else:
    raise ValueError('test_type can be 1 - testing from local folder src/euromod; or 2 - testing from installed package site-packages/euromod.')
    
from euromod import Model
    

PATH_EUROMODFILES = r"C:\Users\iribe\WORK\EUROMOD\EUROMOD_RELEASES_I5.0+"
ID_DATASET = "PL_2020_b2.txt"   
PATH_DATA = os.path.join(PATH_EUROMODFILES, "Input")
# PATH_OUTPUT = os.path.join(PATH_EUROMODFILES, "Output")
# ID_SYSTEM = "PL_2021"
# COUNTRY = 'PL'


# mod =Model(PATH_EUROMODFILES,countries=["PL","HR"])
# EM =Model(PATH_EUROMODFILES, countries = 'PL')
mod =Model(PATH_EUROMODFILES)

# display available countries in euromod
mod.countries
mod[0].name
mod['PL'].name
# load country
mod[21].load()
mod.countries['PL'].load()

mod.countries['PL']

for sysobj in mod[21].systems:
    print([sysobj.name, sysobj.bestMatchDatasets, sysobj.currencyParam])


# data=mod[0].load_data('PL_2020_b2', PATH_DATA = PATH_DATA)
data = pd.read_csv(os.path.join(PATH_DATA, "PL_2020_b2.txt"),sep="\t")
out=mod['PL']['PL_2022'].run(data,"PL_2020_b2.txt")

print('Testing simulations run in a loop...')
out=[]
for sysnam in ['PL_2021','PL_2022']:
     out.append(mod['PL'][sysnam].run(data,"PL_2020_b2.txt"))


print('Testing simulation run with constantsToOverwrite...')
out = mod['PL']['PL_2022'].run(data,"PL_2020_b2.txt",constantsToOverwrite = {("$f_h_cpi","2022"):'10000'})


print('Testing simulation run with addons...')
out = mod['PL']['PL_2022'].run(data,"PL_2020_b2.txt",addons = [("LMA","LMA_PL")])

print('Testing simulation run with switches...')
out = mod['PL']['PL_2022'].run(data,"PL_2020_b2.txt",switches = [("LMA_DATA",True)])

