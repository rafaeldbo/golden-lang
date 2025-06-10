from abc import ABC, abstractmethod
from typing import Union, Tuple, List

from symbol_table import SymbolTable, Symbol

class EvaluationException(Exception):
    pass

class Node(ABC):
    value: Union[str, float]
    children: Tuple['Node']
    queue: List[Tuple['Node', SymbolTable]] = []
    
    def __init__(self, value:Union[str, float, bool], *children:Tuple['Node']) -> None:
        self.value = value
        self.children = children
    
    @abstractmethod
    def evaluate(self, st:SymbolTable) -> Union[Symbol, None]:
        pass
    
    # @abstractmethod
    def generate(self) -> Union[str, None]:
        print(F"Generating code for {self.__class__.__name__} not implemented")
        pass
    
    @staticmethod
    def await_evaluate(node:'Node', st:SymbolTable) -> None:
        Node.queue.append((node, st))
        
    @staticmethod
    def late_evaluate() -> None:
        for node, st in Node.queue:
            node.late_evaluate(st)
        Node.queue.clear()
    
    def __str__(self) -> str:
        if len(self.children) == 0:
            return f"{self.__class__.__name__}({self.value})"
        return f"{self.__class__.__name__}({self.value}, {self.children})"