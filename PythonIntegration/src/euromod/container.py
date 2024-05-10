class Container:
    """
    This class is a container for objects that allow for indexing and representation in multiple ways:
    via keys that are the name of the objects 
    or via integer indexing as in a list.
    """
    def __init__(self):
        self.containerDict = {}
        self.containerList = []

    def __repr__(self):
        s= ""
        for k,v in self.containerDict.items():
            s += k + "\n"
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