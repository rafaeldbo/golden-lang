import json
from typing import Dict

from .symbol_types import Symbol

def serialize_SymbolTable(st: 'SymbolTable') -> Dict:
    serialized = {key: symbol for key, symbol in st.table.items() if key != "__childs__"} 
    serialized["__children__"] = []
    for child in st.children.values():
        serialized_child = serialize_SymbolTable(child)
        if serialized_child is not None:
            serialized["__children__"].append(serialized_child)
    if len(serialized) > 1 or len(serialized["__children__"]) > 0:
        return {st.name: serialized}

class SymbolTable:
    table: Dict[str, Symbol]
    parent: 'SymbolTable'
    children: Dict[str, 'SymbolTable'] 
    id: int = 0
    
    def __init__(self, parent:'SymbolTable'=None, name:str=None) -> None:
        self.name = f"{name}#{SymbolTable.get_id()}" if name else f"SymbolTable#{SymbolTable.get_id()}"
        self.table = {}
        self.parent = parent
        
        self.children = {}
        if parent is not None:
            self.parent.children[self.name] = self
            
    @staticmethod
    def get_id() -> int:
        id = SymbolTable.id
        SymbolTable.id += 1
        return id
            
    def sys_create(self, key:str, var_type:str, value:Symbol=None) -> None:
        if value is not None:
            if var_type != value.type:
                raise TypeError(f"Type mismatch for '{key}': expected '{var_type}', got '{value.type}'")
            self.table[key] = Symbol(var_type, value.value)
        else:
            self.table[key] = Symbol(var_type)
        
    def create(self, key:str, var_type:str, value:Symbol=None) -> None:
        if key in self.table:
            raise NameError(f"Name '{key}' is already defined")
        elif key.startswith("__") and key.endswith("__"):
            raise NameError(f"Name '{key}' is a reserved keyword and cannot be used")
   
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
    
    def __str__(self) -> str:
        serialized_st = serialize_SymbolTable(self)
        if serialized_st is not None:
            return json.dumps(serialized_st, indent=3, default=lambda obj: repr(obj))
        return ""