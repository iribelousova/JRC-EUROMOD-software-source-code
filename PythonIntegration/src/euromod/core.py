import os
import time
import pandas as pd

from utils._paths import CWD_PATH, DLL_PATH
import clr as clr
import System as SystemCs
from utils.clr_array_convert import asNetArray,asNumpyArray
from utils.utils import is_iterable
clr.AddReference(os.path.join(DLL_PATH, "EM_Executable.dll" ))
from EM_Executable import Control
clr.AddReference(os.path.join(DLL_PATH, "EM_XmlHandler.dll" ))
from EM_XmlHandler import CountryInfoHandler,TAGS

from info import Info
from container import Container
from typing import Dict, Tuple, Optional, Any, List


class Model():
    """
    Model - a Python library for the microsimulation model EUROMOD.
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
    
    
    def __init__(self, model_path : str, countries = None):
        """
        

        Parameters
        ----------
        model_path : str
            path to the EUROMOD model.
        countries : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        self.model_path =  model_path
        self.countries = CountryContainer()
        
        if countries == None:
            countries = os.listdir(os.path.join(model_path,'XMLParam','Countries'))
            self._load_country(countries)
        else:
            countries_preload = os.listdir(os.path.join(model_path,'XMLParam','Countries'))
            self._load_country(countries_preload)
            for country in countries: #For countries explicitly demanded, load xmlInfoHandler already
                self.countries[country].load()
                
        
        
    def _load_country(self, countries):        
        """
        Load objects of the TAGS.CONFIG_COUNTRY class.

        Parameters:
        -----------------------------------------------------------------------
            countries   : (str, list of str) 
                        The two-letters country codes (ex: ['IT','LV']).


       
        """

        if type(countries) not in [str, list, set]:
            raise TypeError("Parameter 'countries' must be str, list or set.")
        if type(countries) == str:
            countries = [countries]
            
    	### loop over countries to add the country containers
        for country in countries:            
            ### "Country" class is country specific
            self.countries.add(country,self)

    def __getitem__(self, country):
        return self.countries[country]
    
                


class Country():

    def __init__(self,country: str,model: str):
        self.name = country    
        self.model = model
        
        
    def load(self):
        self._countryInfoHandler = CountryInfoHandler(self.model.model_path, self.name)
        self._load_systems()
        
    def _load_systems(self):
        self.systems = SystemContainer()
        for system in self._countryInfoHandler.GetSystems():
            self.systems.add(system,self)
    def load_data(self, ID_DATASET, PATH_DATA = None):
        if PATH_DATA == None:
            PATH_DATA = os.path.join(self.model.model_path, 'Input')
            
        fname = ID_DATASET + ".txt"    
        df = pd.read_csv(os.path.join(PATH_DATA, fname),sep="\t")
        df.attrs[TAGS.CONFIG_ID_DATA] = ID_DATASET
        df.attrs[TAGS.CONFIG_PATH_DATA] = PATH_DATA
        return df
        
    def get_system_info(self,systems):
        if type(systems) == str:
            return(Info(self._countryInfoHandler.GetSystemExpandedInfo(systems)))
        if type(systems) == list:
            return [Info(self._countryInfoHandler.GetSystemExpandedInfo(system)) for system in systems]
        
        raise("input type for systems argument not supported")     
          
                        
    def __getitem__(self, system):
        return self.systems[system]
    
    
    def __repr__(self):
        return f"Country {self.name}"

        
class SystemContainer(Container):
    def add(self,name,country):
        sysObject = System(name,country)
        self.containerDict[name] = sysObject
        self.containerList.append(sysObject)
        
        

class CountryContainer(Container):
    def add(self,name,model):
        countryObject = Country(name,model)
        self.containerDict[name] = countryObject
        self.containerList.append(countryObject)

            

class System():
    def __init__(self, sysname, country):
        '''
        System class. representing a EUROMOD class
        
        Attributes:
        -----------------------------------------------------------------------
            simulations     : (dict),
                                Keys are simulation names. 
                                Values are objects of the "Simulation" class.
                                Note: simulation names are assigned iteratively.
                                To change simulation name call
                                        obj.systems['sysname'].rename_simulations()

                                
        Methods:
        -----------------------------------------------------------------------
            rename_simulations  : Rename simulation names.
            run                 : Run EUROMOD simulation.
                
        '''  
        self.name =  sysname
        self.country = country
        self._setinfo()
        
    def _setinfo(self):
        info = self.country._countryInfoHandler.GetSystemExpandedInfo(self.name)
        for el in info:
            key = el.Key
            if key != "id": # Lower first letter if not equal to ID
                key = key[0].lower() + key[1:]
            value = el.Value
            if key in ['bestMatchDatasets','datasets']:
                setattr(self, key, value.split(' '))
            else: 
                setattr(self, key, value)
  
    def _get_dataArray(self, df):
        ### check data format
        if type(df) != pd.core.frame.DataFrame:
            raise TypeError("Parameter 'data' must be a pandas.core.frame.DataFrame.")
        ### converting the numpy array to a DotNet/csharp array        
        dataArr=asNetArray(df.to_numpy().T)
        return dataArr
        
    def _convert_configsettings(self, configSettings):
        ### check configSettings format
        if type(configSettings) != dict:
            raise TypeError("Parameter 'configSettings' must be dict.")
        ### Creation of csharp dictionary
        configSettingsDict = SystemCs.Collections.Generic.Dictionary[SystemCs.String,SystemCs.String]()
        for key,value in configSettings.items():
            configSettingsDict[SystemCs.String(key) ] = SystemCs.String(value)
        return configSettingsDict
    
    def _get_variables(self, df):
        #### Initialise Csharp object    
        variables = SystemCs.Collections.Generic.List[SystemCs.String]()
        for col in df.columns:
            variables.Add(col)
        return variables
    
    def _get_constantsToOverwrite(self, new_constdict):

         ### check configSettings format    
        if new_constdict == None:
            constantsToOverwrite = new_constdict
        else:
            if type(new_constdict) == dict:
                constantsToOverwrite = SystemCs.Collections.Generic.Dictionary[SystemCs.Tuple[SystemCs.String, SystemCs.String],SystemCs.String]()
                for keys,value in new_constdict.items():
                    if not is_iterable(keys):
                        raise TypeError("Parameter 'constantsToOverwrite' must be a dictionary, with an iterable containing the constant name and groupnumber as key and a string as value (Example: {('$f_h_cpi','2022'):'1000'}).")
                    key1 = keys[0]
                    key2 = keys[1] if keys[1] != "" else -2147483648

                        
                    csharpkey = SystemCs.Tuple[SystemCs.String, SystemCs.String](key1, key2)
                    constantsToOverwrite[csharpkey] = value

            else: 
                raise TypeError("Parameter 'constantsToOverwrite' must be a dictionary (Example: {('$f_h_cpi','2022'):'1000'}).")
        
        return constantsToOverwrite
    
    def rename_simulations(self, oldname, newname = None):
        """
        Provide either
            - one input (oldname) in dict format, 
                where keys are old names and values are new names, or
            - two inputs (oldname, newname) in str format.
        
        Parameters
        -----------------------------------------------------------------------
            oldname     : (str or dict)
                        If str, simulation old name to be changed.
                        If dict, keys are old names and values are new names.
            newname     : (str), optional
                        New name of the simulation.
        """
        
        if type(oldname) == dict:
            for old, new in oldname.items():
                self.simulations[new] = self.simulations.pop(old)
                self.simulations[new].name = new
        elif (type(oldname) == str):
            if(type(newname) != str):
                raise TypeError("Parameter 'newname' must be str.")
            self.simulations[newname] = self.simulations.pop(oldname)
            self.simulations[newname].name = newname
        else:
            raise TypeError("Parameter 'oldname' must be str (if 2 inputs) or dict (if 1 input). See help.")
                
    def _get_config_settings(self,dataset):
        configsettings = {}
        configsettings[TAGS.CONFIG_PATH_EUROMODFILES] = self.country.model.model_path
        configsettings[TAGS.CONFIG_PATH_DATA] = ""
        configsettings[TAGS.CONFIG_PATH_OUTPUT] = ""
        configsettings[TAGS.CONFIG_ID_DATA] = dataset
        configsettings[TAGS.CONFIG_COUNTRY] = self.country.name
        configsettings[TAGS.CONFIG_ID_SYSTEM] = self.name
        return configsettings
        
        
    def run(self,data: pd.DataFrame,ID_DATASET: str,constantsToOverwrite: Optional[Dict[Tuple[str, str], str]] = None,verbose: bool = True,outputpath: str = "",  addons: List[Tuple[str, str]] = [],  switches: List[Tuple[str, bool]] = [],):
        """
        

        Parameters
        ----------
        data : pd.DataFrame
            input dataframe passed to the EUROMOD model.
        ID_DATASET : str
            ID of the dataset.
        constantsToOverwrite : Optional[Dict[Tuple[str, str], str]], optional
            A list of constants to overwrite. Note that the key is a tuple for which the first element is the name of the constant and the second string the groupnumber
            The default is None.
        verbose : bool, optional
            If True then information on the output will be printed. The default is True.
        outputpath : str, optional
            When an output path is provided, there will be anoutput file generated. The default is "".
        addons : List[Tuple[str, str]], optional
            List of addons to be integrated in the spine, where the first element of the tuple is the name of the Addon
            and the second element is the name of the system in the Addon to be integrated. The default is [].
        switches : List[Tuple[str, bool]], optional
            List of Extensions to be switched on or of. The first element of the tuple is the short name of the Addon.
            The second element is a boolean The default is [].

        Raises
        ------
        Exception
            Exception when simulation does not finish succesfully, i.e. without errors.

        Returns
        -------
        sim : TYPE
            simulation object containing the output and error messages

        """
 
        ### initialize the simulation dictionary
        if hasattr(self, 'simulations') is False:
            self.simulations = {}      
     
        
        configSettings = self._get_config_settings(ID_DATASET)
        if len(ID_DATASET) == 0:
            if TAGS.CONFIG_ID_DATA in data.attrs.keys():
                configSettings[TAGS.CONFIG_ID_DATA] = data.attrs[TAGS.CONFIG_ID_DATA] 
            else:
                configSettings[TAGS.CONFIG_ID_DATA] = ID_DATASET
        else:
            configSettings[TAGS.CONFIG_ID_DATA] = ID_DATASET
        if TAGS.CONFIG_PATH_DATA in data.attrs.keys():
            configSettings[TAGS.CONFIG_PATH_DATA] = data.attrs[TAGS.CONFIG_PATH_DATA]
        else:
            configSettings[TAGS.CONFIG_PATH_DATA] = os.path.join(configSettings[TAGS.CONFIG_PATH_EUROMODFILES], "Input")
            
        configSettings[TAGS.CONFIG_PATH_OUTPUT] = os.path.join(outputpath)
        
        if len(addons) > 0:
            for i,addon in enumerate(addons):
                if not is_iterable(addon):
                    raise(TypeError(str(type(addon)) + " is incorrect type for defining addon"))
                configSettings[TAGS.CONFIG_ADDON + str(i)] = addon[0] + "|" +  addon[1]
        if len(switches) > 0:
            for i,switch in enumerate(switches):
                if not is_iterable(switch):
                    raise(TypeError(str(type(switch)) + " is incorrect type for defining extension switch"))
                status = "on" if switch[1] else "off"
                configSettings[TAGS.CONFIG_EXTENSION_SWITCH + str(i)] = switch[0] + '=' +  status
        
        t = time.time()

        ### get Csharp objects
        dataArr = self._get_dataArray(data)
        configSettings_ = self._convert_configsettings(configSettings)
        variables = self._get_variables(data)  
        constantsToOverwrite_ = self._get_constantsToOverwrite(constantsToOverwrite)      

        os.chdir(DLL_PATH)
        ### run system
        out = Control().RunFromPython(configSettings_, dataArr, variables, \
                                      constantsToOverwrite = constantsToOverwrite_,countryInfoHandler = self.country._countryInfoHandler)
        os.chdir(CWD_PATH)
        sim = Simulation(out, configSettings, constantsToOverwrite) 
        if out.Item1:
            ### load "Simulations" Container
            if verbose:
                print("Simulation: " + sim.name + ", System: " + configSettings["ID_SYSTEM"] + ', Data: ' + configSettings["ID_DATASET"] + '  .. done!   Time to simulate'  + str(time.time()-t) + "s")
        else:
            raise Exception("System: " + configSettings["ID_SYSTEM"] + ', Data: ' + configSettings["ID_DATASET"] + '  .. FAILED!   ')
      
        return sim
    
    def __repr__(self):
        return f"System {self.name}"
    
class OutputContainer(Container):
    def add(self,name,data):
        self.containerDict[name] = data
        self.containerList.append(data)
    def keys(self):
        return self.containerDict.keys()
    def items(self):
        return self.containerDict.items()
    def values(self):
        return self.containerDict.values()
        

class Simulation:

    _count: int = 1

    def __init__(self, out, configSettings, constantsToOverwrite):
        '''
        Simulations class. 
        
        Attributes:
        -----------------------------------------------------------------------
            configSettings        : (dict)
                                    Keys are : PATH_EUROMODFILES, PATH_DATA,
                                    PATH_OUTPUT, ID_DATASET, ID_SYSTEM.
                                    Values must be str.
            constantsToOverwrite  : (dict)
                                    Keys are tuple of two strings,
                                    Values are str with the new value.
                                    i.e. dict{tuple('constant_name','constant_group') : str}
            name                  : (str)
                                    Name of the simulation
            output                : (dict),
                                    K   
        '''  
        self.outputs = OutputContainer()
        
        if constantsToOverwrite is None:
            constantsToOverwrite = {}

        if (out.get_Item1()):
            dataDict = dict(out.get_Item2())
            variableNameDict = dict(out.get_Item3())
            for key in dataDict.keys():

                clr_arr = dataDict[key]
                temp = asNumpyArray(clr_arr)

                outputvars = list(variableNameDict[key])
                self.outputs.add(key, pd.DataFrame(temp, columns=outputvars))

        self.errors = [x.message for x in out.Item4]
        if len(self.errors) > 0:
            for error in self.errors:
                print(error)

        self.configSettings = configSettings.copy()
        self.constantsToOverwrite = constantsToOverwrite.copy()

        self.name = "Sim" + str(self.__class__._count)
        self.__class__._count += 1

    def __repr__(self):
        return f'''
name:                 {self.name}
output:               {self.outputs}

'''       
        


    
    
    
    
    
    
    
    
    
    
    
      
    
    
    
    