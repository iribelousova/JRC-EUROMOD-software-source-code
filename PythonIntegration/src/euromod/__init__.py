import os 
import sys

# ### path to the euromod package
MODEL_PATH = os.path.dirname(__file__)
if MODEL_PATH not in sys.path:
    sys.path.insert(0, MODEL_PATH)
    
from core import Model
from info import Info

with open(os.path.join(MODEL_PATH,'VERSION.txt')) as f:
    __version__ = f.readlines()[0] 

# module level doc-string
__doc__ = """
Euromod - a Python library for the microsimulation model EUROMOD.
===========================================================================

**euromod** is a Python package that runs the microsimulation model EUROMOD
provided by the European Commission - JRC. 

*This package requires the EUROMOD software and model to be installed 
on your device. For more information, please visit:
    https://euromod-web.jrc.ec.europa.eu/download-euromod

EUROMOD:
-------------
is a tax-benefit microsimulation model for the European Union that enables 
researchers and policy analysts to calculate, in a comparable manner, 
the effects of taxes and benefits on household incomes and work incentives 
for the population of each country and for the EU as a whole.

Originally maintained, developed and managed by the Institute for Social and 
Economic Research (ISER) of the University of Essex, since 2021 EUROMOD 
is maintained, developed and managed by the Joint Research Centre (JRC) 
of the European Commission, in collaboration with Eurostat 
and national teams from the EU countries. 
===========================================================================
"""

del os, sys, MODEL_PATH