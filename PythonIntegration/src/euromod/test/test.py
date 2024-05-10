import sys
import os
import pandas as pd

sys.path.insert(0, r"C:\Program Files\...\euromod")
from euromod import Euromod

PATH_EUROMODFILES = r"C:\...\EUROMOD_RELEASES_I5.0+"
ID_DATASET = "PL_2020_b2.txt"   
PATH_DATA = os.path.join(PATH_EUROMODFILES, "Input")


EM = Euromod(PATH_EUROMODFILES, countries = 'PL')
EM['PL'].load_system(['PL_2021', 'PL_2022'])


df2 = pd.read_csv(os.path.join(PATH_DATA, "PL_2019_b3.txt"),sep="\t")

EM['PL']['PL_2022'].run(df2, ID_DATASET = "PL_2019_b3.txt", constantsToOverwrite = {("$f_h_cpi","2022"):'1000'})
EM['PL']['PL_2022'].run(df2, ID_DATASET = "PL_2019_b3.txt")