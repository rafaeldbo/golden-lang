from typing import Union, Tuple, Dict

from symbol_types import Symbol

class SymbolTable:
    table: Dict[str, Symbol]
    parent: 'SymbolTable'
    
    def __init__(self, parent:'SymbolTable'=None) -> None:
        self.table = {}
        self.parent = parent
        
        if parent is not None:
            parent.childs.append(self)
        
    def create(self, key:str, var_type:str, value:Symbol=None) -> None:
        if key in self.table:
            raise NameError(f"Name '{key}' is already defined")
   
        if value is not None:
            if var_type != value.type:
                raise TypeError(f"Type mismatch for '{key}': expected '{var_type}', got '{value.type}'")
            self.table[key] = Symbol(var_type, value.value)
        else:
            self.table[key] = Symbol(var_type)
            
    def __getter(self, key:str) -> Symbol:
        symbol = self.table[key]
        if symbol.value is not None:
            return symbol
        raise ValueError(f"Value for '{key}' is not initialized")
        

    def getter(self, key:str) -> Symbol:
        if key in self.table:
            return self.__getter(key)
        
        parent = self.parent
        while parent is not None:
            if key in parent.table:
                return parent.__getter(key)
            parent = parent.parent
            
        raise NameError(f"Name '{key}' is not defined")
    
    def __setter(self, key:str, symbol:Symbol) -> None:
        if symbol.type not in self.table[key].type:
            raise TypeError(f"Type mismatch for '{key}': expected {self.table[key].type}, got {symbol.type}")
        self.table[key] = symbol
    
    def setter(self, key:str, symbol:Symbol) -> None:
        if key in self.table:
            self.__setter(key, symbol)
            return
        
        parent = self.parent
        while parent is not None:
            if key in parent.table:
                parent.__setter(key, symbol)
                return
            parent = parent.parent
        
        raise NameError(f"Name '{key}' is not defined")