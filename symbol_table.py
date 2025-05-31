from typing import Union, Tuple, Dict

class SymbolTable:
    table: Dict[str, Tuple[str, Union[float, str, bool]]]
    parent: 'SymbolTable'
    
    def __init__(self, parent:'SymbolTable'=None) -> None:
        self.table = {}
        self.parent = parent
        
        if parent is not None:
            parent.childs.append(self)
        
    def create(self, key:str, var_type:str, value:Tuple[str, Union[float, str, bool]]=None) -> None:
        if key in self.table:
            raise NameError(f"Name '{key}' is already defined")
   
        if value is not None:
            if var_type != value[0]:
                raise TypeError(f"Type mismatch for '{key}': expected {var_type}, got {value[0]}")
            self.table[key] = (var_type, value[1], False)
        else:
            self.table[key] = (var_type, None, False)
            
    def __getter(self, key:str) -> Tuple[str, Union[float, str, bool]]:
        value = self.table[key]
        if value[2] or (value[1] is not None):
            return value
        raise ValueError(f"Value for '{key}' is not initialized")
        

    def getter(self, key:str) -> Tuple[str, Union[float, str, bool]]:
        if key in self.table:
            return self.__getter(key)
        
        parent = self.parent
        while parent is not None:
            if key in parent.table:
                return parent.__getter(key)
            parent = parent.parent
            
        raise NameError(f"Name '{key}' is not defined")
    
    def __setter(self, key:str, value:Tuple[str, Union[float, str, bool]]) -> None:
        if value[0] not in self.table[key][0]:
            raise TypeError(f"Type mismatch for '{key}': expected {self.table[key][0]}, got {value[0]}")
        self.table[key] = (value[0], value[1], False)
    
    def setter(self, key:str, value:Tuple[str, Union[float, str, bool]]) -> None:
        if key in self.table:
            self.__setter(key, value)
            return
        
        parent = self.parent
        while parent is not None:
            if key in parent.table:
                parent.__setter(key, value)
                return
            parent = parent.parent
        
        raise NameError(f"Name '{key}' is not defined")