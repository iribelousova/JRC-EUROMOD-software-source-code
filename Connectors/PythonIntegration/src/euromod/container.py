import re
class Container:
    """
    This class is a container for objects that allow for indexing and representation in multiple ways:
    via keys that are the name of the objects 
    or via integer indexing as in a list.
    """
    def __init__(self):
        self.containerDict = {}
        self.containerList = []
    def add(self,key,value):
        self.containerDict[key] = value
        self.containerList.append(value)
    def _short_repr(self):
        if len(self) > 10:
            return f"{len(self)} elements"
        elif len(self) == 0:
            return "0 elements"
        else:
            rep = ""
            for i,el in enumerate(self):
                rep += f"{el._short_repr()}"
                if i < len(self)-1:
                    rep += ", "
        return rep
    def __repr__(self):
        s= ""
        maxlen_name = 0
        maxlen_middle = 0
        end_is_empty = True
        for i,el in enumerate(self.containerList):
            maxlen_name = maxlen_name if len(el.name) + len(str(i)) < maxlen_name else len(el.name) + len(str(i))
            repr_middle = el._container_middle_repr()
            maxlen_middle = maxlen_middle if len(repr_middle) + len(str(i)) < maxlen_middle else len(repr_middle) + len(str(i))
            if len(el._container_end_repr()) > 0:
                end_is_empty = False
        for i,el in enumerate(self.containerList):
            name_repr = el.name + " "*(maxlen_name - len(el.name) -len(str(i)))
            repr_middle = el._container_middle_repr() 
            repr_middle_adj = repr_middle + " "*(maxlen_middle - len(repr_middle)) #pretty pritting adjustment middle text
            if maxlen_middle > 0 + len(str(len(self.containerList))):
                s += f"{i}: {name_repr}     | {repr_middle_adj} "
            else:
                s += f"{i}: {name_repr}" 
            if not end_is_empty:
                s += f"    |    {el._container_end_repr()} \n"
            else:
                s += "\n"
        return s
    def __getitem__(self,arg):
        if (type(arg) == int) | (type(arg) == slice):
            return self.containerList[arg]
        if type(arg) == str:
            return self.containerDict[arg]
        
    def __setitem__(self,k,v):
        if (type(k) == int) | (type(k) == slice):
            self.containerList[k] = v
            return
        if type(k) == str:
            self.containerDict[k] = v
            return
        
        raise(TypeError("Type of key is not supported"))
    def __iter__(self):
        return iter(self.containerList)
    def __len__(self):
        return len(self.containerList)
    def __add__(self,other):
        new_container = Container()
        for k,v in self.containerDict.items():
            new_container.containerDict[k] = v
            
        for el in self.containerList:
            new_container.containerList.append(el)
        
        for k,v in other.containerDict.items():
            new_container.containerDict[k] = v
        for el in other.containerList:
            new_container.containerList.append(el)
        return new_container
        
    def keys(self):
        return self.containerDict.keys()
    def items(self):
        return self.containerDict.items()
    def values(self):
        return self.containerDict.values()
    def find(self,key,pattern,return_children=False,case_insentive=True):
        """
        

        Parameters
        ----------
        key : str
            Name of the attribute or the attribute of a child element that you want to look for
            One can search child elements by using the dot-notation. 
            E.g.: mod["BE"]["BE_2023"].policies.find("functions.name","BenCalc")
        pattern : str
            pattern that you want to match.
        return_children : bool, optional
            When True, the return type will be a Container containing elements of the type for which the find method was used
            When False, the return type will be a Container of the elements of the deepest level specified by the pattern key-word.
            E.g.: mod["BE"]["BE_2023"].policies.find("function)
            The default is False.
        case_insentive : bool, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return _find(self,key,pattern,return_children,case_insentive=True)

def _find(container,key,pattern,return_children=False,case_insentive=True):
    if len(container) == 0:
        return Container()
    if case_insentive:
        flags = re.I
    else:
        flags = 0
    matches = Container()
    if "." in key:
        idx_dot = key.find(".") #If there is a dot then what is before could be a container
        potential_container = key[:idx_dot]
        if hasattr(container[0],potential_container) and isinstance(getattr(container[0],potential_container), Container):
            for el in container:
                if not hasattr(el,potential_container):
                    continue
                matches_children = _find( getattr(el,potential_container),key[idx_dot+1:],pattern,return_children,case_insentive)
                if return_children:
                    matches += matches_children
                else:
                    if len(matches_children) > 0:
                        matches.add(el.ID,el)
        elif not hasattr(container[0],potential_container):
            raise AttributeError(f"There is no attribute of the type Container with the name {potential_container}")
                    
    else:
         for item in container.containerList:
             if re.search(pattern, getattr(item,key),flags=flags):
                 matches.add(item.name,item)           
    return matches
        