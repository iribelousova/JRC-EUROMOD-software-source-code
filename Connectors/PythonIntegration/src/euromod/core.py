import os
import pandas as pd
import numpy as np
from utils._paths import CWD_PATH, DLL_PATH
from base import SystemElement, Euromod_Element, SpineElement
import clr as clr
import System as SystemCs
from utils.clr_array_convert import asNetArray,asNumpyArray
from utils.utils import is_iterable
clr.AddReference(os.path.join(DLL_PATH, "EM_Executable.dll" ))
from EM_Executable import Control
clr.AddReference(os.path.join(DLL_PATH, "EM_XmlHandler.dll" ))
from EM_XmlHandler import CountryInfoHandler,TAGS, ReadCountryOptions,ModelInfoHandler, ReadModelOptions
from container import Container
from typing import Dict, Tuple, Optional, List


class Model:
    """
    Base class of the Euromod Connector instantiating the microsimulation model 
    EUROMOD.
    
    Parameters
    ----------
    model_path : :obj:`str`
        Path to the EUROMOD project.
    countries : :obj:`str`, or :obj:`list` [ :obj:`str` ], optional
        Countries to load from the project folder. Names must be two-letter 
        country codes, see the Eurostat `Glossary:Country codes <https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Country_codes>`_.
        If omitted, will load all the available countries in the project folder.
        Default is None.
        
    Returns
    -------
    core.Model
        A class containing the EUROMOD country models.
    
    Example
    --------
    >>> from euromod import Model
    >>> mod=Model(r"C:\EUROMOD_RELEASES_I6.0+")
    
    .. _Documentation:
        https://github.com/euromod/PythonIntegration/HOWTO.pdf
    """
    
    
    def __init__(self, model_path : str, countries = None):
        """
        :class:`Model` instance for the tax-benefit model EUROMOD.
        """
        self.extensions: list[Extension] | None = None 
        """: A :obj:`list` with :class:`Model` extensions."""
        #: Path to the EUROMOD project
        self.model_path: str = model_path 
        """: Path to the EUROMOD project."""
        self.countries: list[Country] = CountryContainer() #: Container with `core.Country` objects
        """: A :obj:`list` with :class:`Country` objects."""
        self._hasMIH: bool = False;
        if countries == None:
            countries = os.listdir(os.path.join(model_path,'XMLParam','Countries'))
            self._load_country(countries)
        else:
            self._load_country(countries)
            # countries_preload = os.listdir(os.path.join(model_path,'XMLParam','Countries'))
            # self._load_country(countries_preload)
            # for country in countries: #For countries explicitly demanded, load xmlInfoHandler already
            #     self.countries[country].load()
    def __repr__(self):
        return f"Model located in {self.model_path}"
                
                
    def __getattr__(self,name):
        if not self._hasMIH:
            self._modelInfoHandler = ModelInfoHandler(self.model_path)
            self._hasMIH = True
            
        if name == "extensions":
            self._load_extensions()
            return self.extensions
      
        
    def _load_extensions(self):
        
        self.extensions = Container()
        for el in self._modelInfoHandler.GetModelInfo(ReadModelOptions.EXTENSIONS):
            ext = Extension(el.Value,self)
            self.extensions.add(el.Key,ext)
        
        
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
    
                


class Country(Euromod_Element):
    """Country-specific EUROMOD tax-benefit model.
    
    This class instantiates the EUROMOD tax benefit model for a given country.
    A class instance is automatically generated and stored in the attribute  
    :obj:`countries` of the base class :class:`Model`.
    
    This class contains subclasses of type :class:`System`, :class:`Policy`,
    :class:`Dataset` and :class:`Extension`.
    
    Example
    --------
    >>> from euromod import Model
    >>> mod=Model(r"C:\EUROMOD_RELEASES_I6.0+")
    >>> mod.countries[0]    
    """

    def __init__(self,country: str,model: str):
        """Instance of the EUORMOD country-specific tax-benefit model.
        """
        self.name: str = country #: Two-letter country code
        """: Two-letters country code."""
        self.model: Model = model
        """": Returns the base :class:`Model` object."""
        self._hasCIH: bool = False
        self.systems: list[System] | None = None #: Container with `core.System` objects
        """: A :obj:`list` with :class:`System` objects."""
        self.policies: list[Policy] | None = None #: Container with `core.Policy` objects
        """: A :obj:`list` with :class:`Policy` objects."""
        self.datasets: list[Dataset] | None = None #: Container with `core.Dataset` objects
        """: A :obj:`list` with :class:`Dataset` objects."""
        self.local_extensions: list[Extension] | None = None #: Container with `core.Extension` objects
        """: A :obj:`list` with :class:`Extension` objects."""

        
    def _load(self):
        if not self._hasCIH:
            if not Control.TranslateToEM3(self.model.model_path, self.name, SystemCs.Collections.Generic.List[str]()):
                raise Exception("Country XML EM3 Translation failed. Probably provided a non-euromod project as an input-path.")
            self._countryInfoHandler = CountryInfoHandler(self.model.model_path, self.name)
            self._hasCIH = True;
    
    def __getattribute__(self,name):
        if name == "systems" and self.__dict__["systems"] is None:
            self._load()
            self._load_systems()
            return self.systems
        if name == "policies" and self.__dict__["policies"] is None:
            self._load()
            self._load_policies()
            return self.policies
        if name == "datasets" and self.__dict__["datasets"] is None:
            self._load()
            self._load_datasets()
            return self.datasets
        if name == "local_extensions" and self.__dict__["local_extensions"] is None:
            self._load()
            self._load_extensions()
            return self.local_extensions
        return super().__getattribute__(name)
    
        
    def _load_extensions(self):
        self.local_extensions = Container()
        for el in self._countryInfoHandler.GetTypeInfo(ReadCountryOptions.LOCAL_EXTENSION):
            ext = Extension(el.Value,self)
            self.local_extensions.add(el.Key,ext)
    
    def _load_policies(self):
        self.policies = Container()
        for el in self._countryInfoHandler.GetTypeInfo(ReadCountryOptions.POL):
            pol = Policy(el.Value,self)
            self.policies.add(pol.ID,pol)
            self.policies[-1].order = self._countryInfoHandler.GetPieceOfInfo(ReadCountryOptions.SYS_POL,self.systems[-1].ID + pol.ID)["Order"]
        for el in self._countryInfoHandler.GetTypeInfo(ReadCountryOptions.REFPOL):
            ref_pol = ReferencePolicy(el.Value,self)
            self.policies.add(ref_pol.ID,ref_pol)
            self.policies[-1].order = self._countryInfoHandler.GetPieceOfInfo(ReadCountryOptions.SYS_POL,self.systems[-1].ID + ref_pol.ID)["Order"]
        self.policies.containerList.sort(key=lambda x: int(x.order))
        
        
    def _load_datasets(self):
        self.datasets = Container()
        for el in self._countryInfoHandler.GetTypeInfo(ReadCountryOptions.DATA):
            db = Dataset(el.Value,self)
            self.datasets.add(db.name,db)
        
    def _load_systems(self):
        self.systems = Container()
        systems = self._countryInfoHandler.GetTypeInfo(ReadCountryOptions.SYS)
        for sys in systems:
            self.systems.add(sys.Value["Name"],System(sys.Value,self))
        
    def load_data(self, ID_DATASET, PATH_DATA = None):
        """
        Load data as a :class:`pandas.DataFrame` object.

        Parameters
        ----------
            ID_DATASET : :obj:`str` 
                        Name of the dataset excluding extension (Note: must be a `txt` file).   
            PATH_DATA : :obj:`str`, optional
                        Path to the dataset. Default is the PATH_TO_EUROMOD_PROJECT/Input folder.
        
        Returns
        -------
        pandas.DataFrame 
            Dataset is returned as a :class:`pandas.DataFrame` object.
        """
        if PATH_DATA == None:
            PATH_DATA = os.path.join(self.model.model_path, 'Input')
            
        fname = ID_DATASET + ".txt"    
        df = pd.read_csv(os.path.join(PATH_DATA, fname),sep="\t")
        df.attrs[TAGS.CONFIG_ID_DATA] = ID_DATASET
        df.attrs[TAGS.CONFIG_PATH_DATA] = PATH_DATA
        return df
        
          
                        
    def __getitem__(self, system):
        return self.systems[system]
    
    

    def _short_repr(self):
        return f"Country {self.name}"
    def _container_middle_repr(self):
        return ""
        

        
        

class CountryContainer(Container):
    """Container class storing core.Country objects.
    """
    def add(self,name,model):
        countryObject = Country(name,model)
        self.containerDict[name] = countryObject
        self.containerList.append(countryObject)

 

class System(Euromod_Element):   
    """A EUROMOD specific tax-benefit system.
    
    This class instantiates the EUROMOD tax benefit model for a specific system.
    A class instance is automatically generated and stored in the attribute  
    `systems` of class :class:`Country`.
    
    This class contains subclasses of type :class:`DatasetInSystem`, and
    :class:`PolicyInSystem`.
    
    Example
    --------
    >>> from euromod import Model
    >>> mod=Model(r"C:\EUROMOD_RELEASES_I6.0+")
    >>> mod.countries[0].systems[-1]
    """
    def __init__(self,*arg):
        super().__init__(*arg)
        self.ID: str = ""
        """Identifier number of the system."""
        self.comment: str = ""
        """Comment specific to the system."""
        self.currencyOutput: str = ""
        """Currency of the simulation results."""
        self.currencyParam: str = ""
        """Currency of the monetary parameters in the system."""
        self.headDefInc: str = ""
        """Main income definition."""
        self.name: str = ""
        """Name of the system."""
        self.order: str = ""
        """System order in the spine."""
        self.private: str = ""
        """Access type."""
        self.year: str = ""
        """System year."""
        self.datasets: list[DatasetInSystem] | None = None
        """: A :obj:`list` of :class:`DatasetInSystem` objects in the system."""
        self.policies: list[PolicyInSystem] | None = None
        """: A :obj:`list` of :class:`PolicyInSystem` objects in the system."""
        self.bestmatch_datasets: list[Dataset] | None = None
        """: A :obj:`list` with best-match :class:`Dataset` objects in the system."""
    def __getattribute__(self,name):
        if name == 'policies' and self.__dict__["policies"] is None:
            self._load_policies()
            return self.policies
        if name == 'datasets' and self.__dict__["datasets"] is None:
            self._load_datasets()
            return self.datasets
        if name == 'bestmatch_datasets' and self.__dict__["bestmatch_datasets"] is None:
            self._load_bestmatchdatasets()
            return self.bestmatch_datasets
        
        return super().__getattribute__(name)
    def _load_bestmatchdatasets(self):
        self.bestmatch_datasets = Container()
        for x in self.datasets:
            if x.bestMatch == "yes":
                self.bestmatch_datasets.add(x.name,x)
             
    def _load_datasets(self):
        self.datasets = Container()
        for dataset in self.parent.datasets:
            id = self.ID + dataset.ID
            sysdata = self.parent._countryInfoHandler.GetPieceOfInfo(ReadCountryOptions.SYS_DATA,id)
            if len(sysdata) > 0:
                self.datasets.add(id,DatasetInSystem(sysdata, id, self, dataset))
    def _load_policies(self):
        self.policies = Container()
        for pol in self.parent.policies:
            id = self.ID + pol.ID
            syspol = self.parent._countryInfoHandler.GetPieceOfInfo(ReadCountryOptions.SYS_POL,id)
            self.policies.add(id,PolicyInSystem(syspol, id, self, pol))
    def _get_dataArray(self, df):
        ### check data format
        if type(df) != pd.core.frame.DataFrame:
            raise TypeError("Parameter 'data' must be a pandas.core.frame.DataFrame.")
        ### converting the numpy array to a DotNet/csharp array        
        dataArr=asNetArray(df.to_numpy(np.float64).T)
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
    

                
    def _get_config_settings(self,dataset):
        configsettings = {}
        configsettings[TAGS.CONFIG_PATH_EUROMODFILES] = self.parent.model.model_path
        configsettings[TAGS.CONFIG_PATH_DATA] = ""
        configsettings[TAGS.CONFIG_PATH_OUTPUT] = ""
        configsettings[TAGS.CONFIG_ID_DATA] = dataset
        configsettings[TAGS.CONFIG_COUNTRY] = self.parent.name
        configsettings[TAGS.CONFIG_ID_SYSTEM] = self.name
        return configsettings
        
        
    def run(self,data: pd.DataFrame,dataset_id: str,constantsToOverwrite: Optional[Dict[Tuple[str, str], str]] = None,verbose: bool = True,outputpath: str = "",  addons: List[Tuple[str, str]] = [],  switches: List[Tuple[str, bool]] = [],nowarnings=False):
        """Run the simulation of a EUROMOD tax-benefit system.
        

        Parameters
        ----------
        data : :class:`pandas.DataFrame`
            input dataframe passed to the EUROMOD model.
        dataset_id : :obj:`str`
            ID of the dataset.
        constantsToOverwrite : Optional[ :obj:`dict` [ :obj:`tuple` [ :obj:`str`, :obj:`str` ], :obj:`str` ]], optional
            A :obj:`list` of constants to overwrite. Note that the key is a tuple for which the first element is the name of the constant and the second string the groupnumber
            Default is :obj:`None`.
        verbose : :obj:`bool`, optional
            If True then information on the output will be printed. Default is :obj:`True`.
        outputpath : :obj:`str`, optional
            When an output path is provided, there will be anoutput file generated. Default is "".
        addons : :obj:`list` [ :obj:`tuple` [ :obj:`str`, :obj:`str` ]], optional
            :obj:`list` of addons to be integrated in the spine, where the first element of the tuple is the name of the Addon
            and the second element is the name of the system in the Addon to be integrated. Default is [].
        switches : :obj:`list` [ :obj:`tuple` [ :obj:`str`, :obj:`bool` ]], optional
            :obj:`list` of Extensions to be switched on or of. The first element of the tuple is the short name of the Addon.
            The second element is a boolean Default is [].
        nowarnings : :obj:`bool`, optional
            If True, the warning messages resulting from the simulations will be suppressed. Default is :obj:`False`.

        Raises
        ------
        Exception
            Exception when simulation does not finish succesfully, i.e. without errors.

        Returns
        -------
        core.Simulation 
            A class containing simulation output and error messages.

        Example
        --------
        >>> # Load the dataset
        >>> import pandas as pd
        >>> data = pd.read_csv(r"C:\EUROMOD_RELEASES_I6.0+\Input\sl_demo_v4.txt",sep="\t")
        >>> # Load EUROMOD
        >>> from euromod import Model
        >>> mod=Model(r"C:\EUROMOD_RELEASES_I6.0+")
        >>> # Run simulation
        >>> out=mod.countries['SL'].systems['SL_1996'].run(data,'sl_demo_v4')
        """
 
        ### initialize the simulation dictionary
        if hasattr(self, 'simulations') is False:
            self.simulations = {}      
     
        
        configSettings = self._get_config_settings(dataset_id)
        if len(dataset_id) == 0:
            if TAGS.CONFIG_ID_DATA in data.attrs.keys():
                configSettings[TAGS.CONFIG_ID_DATA] = data.attrs[TAGS.CONFIG_ID_DATA] 
            else:
                configSettings[TAGS.CONFIG_ID_DATA] = dataset_id
        else:
            configSettings[TAGS.CONFIG_ID_DATA] = dataset_id
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
        
        
        data = data.select_dtypes(['number'])

        ### get Csharp objects
        dataArr = self._get_dataArray(data)
        configSettings_ = self._convert_configsettings(configSettings)
        variables = self._get_variables(data)  
        constantsToOverwrite_ = self._get_constantsToOverwrite(constantsToOverwrite)      

        os.chdir(DLL_PATH)
        ### run system
        out = Control().RunFromPython(configSettings_, dataArr, variables, \
                                      constantsToOverwrite = constantsToOverwrite_,countryInfoHandler = self.parent._countryInfoHandler)
        os.chdir(CWD_PATH)
        sim = Simulation(out, configSettings, constantsToOverwrite) 
        for error in out.Item4:
            if error.isWarning:
            	print(f"Warning: {error.message}")
            else:
                print(f"Error: {error.message}")
        if out.Item1:
            ### load "Simulations" Container
            if verbose:
                print(f"Simulation for system {self.name} with dataset {dataset_id} finished.")
        else:
            raise Exception(f"Simulation for system {self.name} with dataset {dataset_id} aborted with errors.")
      
        return sim
    
    #def __repr__(self):
     #   return f"System {self.name}"
    def _short_repr(self):
        return f"{self.name}"
    def _container_middle_repr(self):
        return ""
class OutputContainer(Container):
    def add(self,name,data):
        self.containerDict[name] = data
        self.containerList.append(data)
    def __repr__(self):
        s= ""
        for i,el in enumerate(self.containerList):
            s += f"{i}: {repr(el)}\n"
        return s
    
        
class PolicyContainer(Container):
    def add(self,id,policy):
        self.containerDict[id] = policy
        self.containerList.append(policy)

class FunctionContainer(Container):     
    def add(self,id,function):
        self.containerDict[id] = function
        self.containerList.append(function)
        

class Simulation:
    """Object storing the simulation results.
    
    This is a class containing results from the simulation :obj:`run` 
    and other related configuration information. 
    """
    
    def __init__(self, out, configSettings, constantsToOverwrite):
        '''
        A class with results from the simulation :obj:`run`.
        
        Simulation results are stored as :class:`pandas.DataFrame` in the 
        '''  
        self.outputs: list[pd.DataFrame] = OutputContainer()
        """: A :obj:`list` with type :class:`pandas.DataFrame` simulation results. 
            For indexing use an integer or a label from :obj:`output_filenames`."""
        self.output_filenames: list[str] | [] = []
        """ A :obj:`list` of file-names with simulation output."""
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
                self.output_filenames.append(key)

        self.errors: list[str] = [x.message for x in out.Item4]
        """: A :obj:`list` with errors and warnings from the simulation run."""

        self.configSettings: dict[str,str] = configSettings.copy()
        """: A :obj:`dict`-type object with simulation settings."""
        
        self.constantsToOverwrite: dict[tuple(str,str),str] = constantsToOverwrite.copy()
        """: A :obj:`dict`-type object with user-defined constants."""


    def __repr__(self):
        return f'''
output:               {self.outputs}

'''       




class Dataset(Euromod_Element):
    """Datasets available in a country model.
    """
    _objectType = ReadCountryOptions.DATA

    def _short_repr(self):
        return f"{self.name}"
    def _container_middle_repr(self):
        return ""
    def __init__(self,*args): 
        self.ID: str = ""
        """: Dataset identifier number."""
        self.coicopVersion: str = ""
        """: COICOP  version."""
        self.comment: str = ""
        """: Comment  about the dataset."""
        self.currency: str = ""
        """: Currency of the monetary values in the dataset."""
        self.decimalSign: str = ""
        """: Decimal sign"""
        self.name: str = ""
        """: Name of the dataset."""
        self.private: str = "no"
        """: Access type."""
        self.readXVariables: str = "no"
        """: Read variables."""
        self.useCommonDefault: str = "no"
        """: Use default."""
        self.yearCollection: str = ""
        """: Year of the dataset collection."""
        self.yearInc: str = ""
        """: Reference year for the income variables."""
        super().__init__(*args)
                

class Policy(SpineElement):
    """Policy rules modeled in a country.
    """
    _objectType = ReadCountryOptions.POL
    _extensionType = ReadCountryOptions.EXTENSION_POL
    def _load_functions(self):
        self.functions = FunctionContainer()
        functions = self.parent._countryInfoHandler.GetPiecesOfInfo(ReadCountryOptions.FUN,TAGS.POL_ID,self.ID)
        for fun in functions:
            self.functions.add(fun["ID"] ,Function(fun,self))
            self.functions[-1].order = self.parent._countryInfoHandler.GetPieceOfInfo(ReadCountryOptions.SYS_FUN,self.parent.systems[0].ID + fun["ID"])["Order"]
        
        self.functions.containerList.sort(key=lambda x: int(x.order))

    def _container_middle_repr(self):
        ext = self._get_extension_repr()
        
        return f"{ext}"
    def _container_end_repr(self):
        
        comment = self.comment if len(self.comment) < 50 else self.comment[:50] + " ..."
        
        return f"{comment}"
    
    def __getattribute__(self, name):
        if name == "extensions" and self.__dict__["extensions"] is None:
            self._linkToExtensions()
            return self.extensions
        if name == "functions" and self.__dict__["functions"] is None:
            self._load_functions()
            return self.functions
        return super().__getattribute__(name)

    def __init__(self,*arg):
        self.private: str = "no"
        """: Access type. Default is 'no'."""
        self.functions: list[Function] | None = None
        """: A :obj:`list` of policy-specific :class:`Function` objects."""
        self.extensions: list[Extension] | None = None
        """: A :obj:`list` of policy-specific :class:`Extension` objects."""
        self.ID: str = ""
        """Identifier number of the policy."""
        self.comment: str = ""
        """Comment specific to the policy."""
        self.name: str = ""
        """Name of the policy."""
        self.order: str = ""
        """Order of the policy in the specific spine."""
        self.spineOrder: str = ""
        """Order of the policy in the spine."""
        super().__init__(*arg)
         
    
class ReferencePolicy(SpineElement):
    """Object storing the reference policies."""
    _objectType = ReadCountryOptions.REFPOL
    def __init__(self,info,parent):
        super().__init__(info,parent) #take the parent constructor
        #get name of the reference policy using RefPolID
        self.name: str = self.parent._countryInfoHandler.GetPieceOfInfo(ReadCountryOptions.POL,self.refPolID)["Name"]
        """: Name of the reference policy."""
        self.extensions: list[Extension] | None = None
        """: A :obj:`list` of reference policy-specific :class:`Extension` objects."""


    def _short_repr(self):
        return f"Reference Policy: {self.name}"
    def _container_middle_repr(self):
        return "Reference Policy"
    def _container_begin_repr(self):
        return f"Reference Policy: {self.name}"
    def __getattribute__(self, name):
        if name == "extensions" and self.__dict__["extensions"] is None:
            self._linkToExtensions()
            return self.extensions
        return super().__getattribute__(name)

           

class Function(SpineElement):
    """Functions implemented in a country policy.
    """
    _objectType = ReadCountryOptions.FUN
    _extensionType = ReadCountryOptions.EXTENSION_FUN

    def _short_repr(self):
        ext = self._get_extension_repr()
        return f"{self.name}{ext}"
    def _container_middle_repr(self):
        ext = self._get_extension_repr()
        return ext
    def _container_end_repr(self):
        comment = self.comment if len(self.comment) < 50 else self.comment[:50] + " ..."
        return  comment
    
    def _load_parameters(self):
        self.parameters = Container()
        parameters = self.parent.parent._countryInfoHandler.GetPiecesOfInfo(ReadCountryOptions.PAR,TAGS.FUN_ID,self.ID) #Returns an Iterable of Csharp Dictionary<String,String>
        for par in parameters:
            self.parameters.add(par["ID"] ,Parameter(par,self))
            self.parameters[-1].order = self.parent.parent._countryInfoHandler.GetPieceOfInfo(ReadCountryOptions.SYS_PAR,self.parent.parent.systems[0].ID + par["ID"])["Order"]
        self.parameters.containerList.sort(key=lambda x: int(x.order))
    
    def __getattribute__(self, name):
        if name == "extensions" and self.__dict__["extensions"] is None:
            self._linkToExtensions()
            return self.extensions
        if name == "parameters" and self.__dict__["parameters"] is None:
            self._load_parameters()
            return self.parameters
        return super().__getattribute__(name)
    def __init__(self,*arg):
        self.ID: str = ""
        """Identifier number of the function."""
        self.comment: str = ""
        """Comment specific to the function."""
        self.name: str = ""
        """Name of the function."""
        self.order: str = ""
        """Order of the function in the specific spine."""
        self.polID: str = ""
        """Identifier number of the reference policy."""
        self.private: str = "no"
        """Access type."""
        self.spineOrder: str = ""
        """Order of the function in the spine."""
        self.parameters: list[Parameter] | None = None
        """: A :obj:`list` of :class:`Parameter` objects in a country."""
        self.extensions: list[Extension] | None = None
        """: A :obj:`list` of :class:`Extension` objects in a country."""
        super().__init__(*arg)

class Parameter(SpineElement):
    """Parameters set up in a function.
    """
    _objectType = ReadCountryOptions.PAR
    _extensionType = ReadCountryOptions.EXTENSION_PAR
    def _container_middle_repr(self):
        ext = self._get_extension_repr()
        return f"{ext}"
    def _container_end_repr(self):
        comment = self.comment if len(self.comment) < 50 else self.comment[:50] + " ..."
        return  f"{comment}"
    def __getattr__(self,name):
        if name == "extensions":
            self._linkToExtensions()
            return self.extensions
        raise AttributeError();   
    def __getattribute__(self, name):
        if name == "extensions" and self.__dict__["extensions"] is None:
            self._linkToExtensions()
            return self.extensions

        return super().__getattribute__(name)
    def __init__(self,*arg):
        self.group: str = ""
        """str: Parameter group number."""
        self.extensions: list[Extension] | None = None
        """: A :obj:`list` with :class:`Extension` objects."""
        self.ID: str = ""
        """Identifier number of the parameter."""
        self.comment: str = ""
        """Comment specific to the parameter."""
        self.funID: str = ""
        """Identifier number of the reference function at country level."""
        self.name: str = ""
        """Name of the parameter."""
        self.order: str = ""
        """Order of the parameter in the specific spine."""
        self.spineOrder: str = ""
        """Order of the parameter in the spine."""
        super().__init__(*arg)


class PolicyInSystem(SystemElement):
    """Policy rules modeled in a system.
    """
    _objectType = ReadCountryOptions.SYS_POL
    def __init__(self,*arg):
        super().__init__(*arg)
        self.functions: list[FunctionInSystem] | None = None
        """: A :obj:`list` with :class:`FunctionInSystem` objects specific to the system"""
        self.private: str = "no"
        """: Access type. Default is 'no'."""
        self.extensions: list[Extension] | None = None
        """: A :obj:`list` of policy-specific :class:`Extension` objects."""
        self.ID: str = ""
        """Identifier number of the policy."""
        self.comment: str = ""
        """Comment specific to the policy."""
        self.name: str = ""
        """Name of the policy."""
        self.order: str = ""
        """Order of the policy in the specific spine."""
        self.spineOrder: str = ""
        """Order of the policy in the spine."""
        self.polID: str = ""
        """Identifier number of the reference policy at country level."""
        self.sysID: str = ""
        """Identifier number of the reference system."""
        self.switch: str = ""
        """Policy switch action."""
        
    def _container_middle_repr(self):
        ext = self._get_extension_repr()
        return f"{self.switch}{ext}" 
    def _container_end_repr(self):
        if type(self.parentTypeObject) == Policy:
            comment = self.comment if len(self.comment) < 50 else self.comment[:50] + " ..."
        else:
            comment = ""
        return  f"{comment}"
    def __getattribute__(self, name):
        if name == "functions" and self.__dict__["functions"] is None:
            self._load_functions()
            return self.functions
        return super().__getattribute__(name)

        
    def _load_functions(self):
        self.functions = FunctionContainer()
        sys = self.parentSystem
        for fun in self.parentTypeObject.functions:
            id = sys.ID + fun.ID
            sysfun = self.parentSystem.parent._countryInfoHandler.GetPieceOfInfo(ReadCountryOptions.SYS_FUN,id)
            self.functions.add(id,FunctionInSystem(sysfun, id, sys, fun))
            
class ParameterInSystem(SystemElement):
    """Parameters set up in a function for a specific system.
    """
    _extensionType = ReadCountryOptions.EXTENSION_PAR
    _ctryOption = ReadCountryOptions.SYS_PAR
    
    def __init__(self):
        self.group: str = ""
        """str: Parameter group number."""
        self.extensions: list[Extension] | None = None
        """: A :obj:`list` with :class:`Extension` objects."""
        self.ID: str = ""
        """Identifier number of the parameter."""
        self.comment: str = ""
        """Comment specific to the parameter."""
        self.funID: str = ""
        """Identifier number of the reference function at country level."""
        self.name: str = ""
        """Name of the parameter."""
        self.order: str = ""
        """Order of the parameter in the specific spine."""
        self.spineOrder: str = ""
        """Order of the parameter in the spine."""
        self.parID: str = ""
        """Identifier number of the reference parameter at country level."""
        self.sysID: str = ""
        """Identifier number of the reference system."""
        self.value: str = ""
        """Value of the parameter."""

    def _short_repr(self):
        return f"{self.parentTypeObject.name}" 
    def _container_middle_repr(self):
        return f"{self.value}" 
    def _container_end_repr(self):
        comment = self.comment if len(self.comment) < 50 else self.comment[:50] + " ..."
        return  f"{comment}"
    
class DatasetInSystem(SystemElement):
    """Datasets available in a system model.
    """
    def __init__(self): 
        self.ID: str = ""
        """: Dataset identifier number."""
        self.bestMatch: str = ""
        """: If yes, the current dataset is a best match for the specific system."""
        self.coicopVersion: str = ""
        """: COICOP  version."""
        self.comment: str = ""
        """: Comment  about the dataset."""
        self.currency: str = ""
        """: Currency of the monetary values in the dataset."""
        self.dataID: str = ""
        """: Identifier number of the reference dataset at the country level."""
        self.decimalSign: str = ""
        """: Decimal sign"""
        self.name: str = ""
        """: Name of the dataset."""
        self.private: str = "no"
        """: Access type."""
        self.readXVariables: str = "no"
        """: Read variables."""
        self.sysID: str = ""
        """: Identifier number of the reference system."""
        self.useCommonDefault: str = "no"
        """: Use default."""
        self.yearCollection: str = ""
        """: Year of the dataset collection."""
        self.yearInc: str = ""
        """: Reference year for the income variables."""
        
    _ctryOption = ReadCountryOptions.SYS_DATA
    def _container_middle_repr(self):
        if self.bestMatch == "yes":
            return  "best match"
        else:
            return ""
    
class FunctionInSystem(SystemElement):
    """Function implemented in a policy for a specific system.
    """
    _ctryOption = ReadCountryOptions.SYS_FUN 
    def __init__(self,*arg):
        self.ID: str = ""
        """Identifier number of the function."""
        self.comment: str = ""
        """Comment specific to the function."""
        self.funID: str = ""
        """Identifier number of the reference function at country level."""
        self.name: str = ""
        """Name of the function."""
        self.order: str = ""
        """Order of the function in the specific spine."""
        self.polID: str = ""
        """Identifier number of the reference policy."""
        self.private: str = "no"
        """Access type."""
        self.spineOrder: str = ""
        """Order of the function in the spine."""
        self.switch: str = ""
        """: Policy switch action."""
        self.sysID: str = ""
        """: Identifier number of the reference policy."""
        self.extensions: list[Extension] | None = None
        """: A :obj:`list` of :class:`Extension` objects in a country."""
        self.parameters: list[ParameterInSystem] | None = None
        """: A :obj:`list` with :class:`ParameterInSystem` objects specific to a function."""
        super().__init__(*arg)
    
    def _container_middle_repr(self):
        ext = self._get_extension_repr()
        return f"{self.switch}{ext}" 
    def _container_end_repr(self):
        comment = self.comment if len(self.comment) < 50 else self.comment[:50] + " ..."
        return  f"{comment}"
    def __getattribute__(self, name):
        if name == "parameters" and self.__dict__["parameters"] is None:
            self._load_parameters()
            return self.parameters
        return super().__getattribute__(name)
    def _load_parameters(self):
       self.parameters = Container()
       sys = self.parentSystem
       for par in self.parentTypeObject.parameters:
           id = sys.ID + par.ID
           syspar = self.parentSystem.parent._countryInfoHandler.GetPieceOfInfo(ReadCountryOptions.SYS_PAR,id)
           self.parameters.add(id,ParameterInSystem(syspar, id, sys, par))

class Extension(Euromod_Element):
    """EUROMOD built-in extensions. 
    """
    _objectType = ReadModelOptions.EXTENSIONS
    
    def __init__(self):
        self.name: str = ""
        """Full name of the extension."""
        self.shortName: str = ""
        """Short name of the extension."""
        
    def __repr__(self):
        return f"Extension: {self.name}" 

    def _short_repr(self):
        return f"{self.shortName}" 
    def _container_middle_repr(self):
        return  ""
    


    



