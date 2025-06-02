from abc import ABC, abstractmethod
from typing import Union, Tuple

from symbol_table import SymbolTable, Symbol

class EvaluationException(Exception):
    pass

class Node(ABC):
    value: Union[str, float]
    children: Tuple['Node']
    
    def __init__(self, value:Union[str, float, bool], *children:Tuple['Node']) -> None:
        self.value = value
        self.children = children
    
    @abstractmethod
    def evaluate(self, st:SymbolTable) -> Union[Symbol, None]:
        pass
    
    def __str__(self) -> str:
        if len(self.children) == 0:
            return f"{self.__class__.__name__}({self.value})"
        return f"{self.__class__.__name__}({self.value}, {self.children})"