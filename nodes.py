from abc import ABC, abstractmethod
from typing import Union, List, Tuple

from symbol_table import SymbolTable

NUMBER = "number"
STRING = "string"
BOOLEAN = "boolean"
DATE = "date"
TIME = "time"
LIST = "list"

class EvaluationException(Exception):
    pass

class Node(ABC):
    value: Union[str, float]
    children: List['Node']
    
    def __init__(self, value:Union[str, float, bool], *children:List['Node']) -> None:
        self.value = value
        self.children = children
    
    @abstractmethod
    def evaluate(self, st:SymbolTable) -> Union[Tuple[str, Union[float, str, bool]], None]:
        pass


class NoOp(Node):
    def __init__(self,*void:Tuple[Node]) -> None:
        super().__init__(None)
    
    def evaluate(self, st:SymbolTable) -> None:
        pass

    
class BinOp(Node):
    def __init__(self, operation:str, left:Node, right:Node):
        super().__init__(operation, left, right)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, Union[float, str, bool]]:
        left = self.children[0].evaluate(st)
        right = self.children[1].evaluate(st)
        if left[0] == STRING or right[0] == STRING:
            if self.value == "plus":
                return (STRING, left[1] + right[1])
        
        if left[0] != right[0]:
            raise EvaluationException(f"Invalid binary operation: both operands must be of the same type, impossible to do '{left[0]}' {self.value} '{right[0]}'")
        
        if self.value == "equal":
            return (BOOLEAN, left[1] == right[1])
        elif self.value == "greater":
            return (BOOLEAN, left[1] > right[1])
        elif self.value == "less":
            return (BOOLEAN, left[1] < right[1])
        
        if left[0] == NUMBER:
            if self.value == "plus":
                return (NUMBER, left[1] + right[1])
            elif self.value == "minus":
                return (NUMBER, left[1] - right[1])
            elif self.value == "mult":
                return (NUMBER, left[1] * right[1])
            elif self.value == "div":
                return (NUMBER, left[1] // right[1])
            
        if left[0] == BOOLEAN:
            if self.value == "and":
                return (BOOLEAN, left[1] and right[1])
            elif self.value == "or":
                return (BOOLEAN, left[1] or right[1])
            
        raise EvaluationException(f"Invalid binary operation: cannot operate '{left[0]}' {self.value} '{right[0]}'")
    
class UnOp(Node):
    def __init__(self, operation:str, unary:Node):
        super().__init__(operation, unary)
        
    def evaluate(self, st:SymbolTable) -> float:
        child = self.children[0].evaluate(st)
        
        if child[0] == NUMBER and self.value == "minus":
            return (NUMBER, -child[1])
        elif child[0] == BOOLEAN and self.value == "not":
            return (BOOLEAN, not child[1])
        
        raise EvaluationException(f"Invalid unary operation: {self.value}{child[1]}, cannot do '{self.value}' in '{child[0]}'")
    
class NumberValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, float]:
        return (NUMBER, self.value)
    
class StringValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, str]:
        return (STRING, self.value)
    
class BooleanValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, bool]:
        return (BOOLEAN, self.value)
    
class DateValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, str]:
        return (DATE, self.value)
    
class TimeValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, str]:
        return (TIME, self.value)
    
class ListValue(Node):
    def __init__(self, void, values:Tuple[Node]):
        super().__init__("list", values)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, List[Union[float, str, bool]]]:
        return (LIST, [child.evaluate(st)[1] for child in self.children])
    
class Identifier(Node):
    def __init__(self, identifier:str, *void:Tuple[Node]):
        super().__init__(identifier)
    
    def evaluate(self, st:SymbolTable) -> Union[float, str, bool]:
        return st.getter(self.value)

class Variable(Node):
    def __init__(self, var_type:str, identifier:Identifier, expression:Node=NoOp()):
        super().__init__(var_type, identifier, expression)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.create(self.children[0].value, self.value, self.children[1].evaluate(st))
    
class Assignment(Node):
    def __init__(self, void, identifier:Identifier, expression:Node):
        super().__init__("assign", identifier, expression)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.setter(self.children[0].value, self.children[1].evaluate(st))

class Block(Node):
    def __init__(self, void, *statements:Tuple[Node]):
        super().__init__("block", *statements)
    
    def evaluate(self, st:SymbolTable) -> None:
        for child in self.children:
            child.evaluate(st)

class Display(Node):
    def __init__(self, void, identifier:Node, printable_expression:Node):
        super().__init__("display", identifier, printable_expression)
    
    def evaluate(self, st:SymbolTable) -> None:
        print(f"on {self.children[0].value}:", self.children[1].evaluate(st)[1])
    
    
class IfOp(Node):
    def __init__(self, void, condition:Node, if_block:Node, else_block:Node=None):
        super().__init__("if", condition, if_block, else_block)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, Union[float, str, bool]]:
        child = self.children[0].evaluate(st)
        if child[0] != BOOLEAN:
            raise EvaluationException(f"Invalid condition: expected 'bool', got '{child[0]}'")
        
        if child[1]:
            return self.children[1].evaluate(st)
            
        elif self.children[2] is not None:
            return self.children[2].evaluate(st)
    
class WhileOp(Node):
    def __init__(self, void, condition:Node, block:Node):
        super().__init__("while", condition, block)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, Union[float, str, bool]]:
        child = self.children[0].evaluate(st)
        if child[0] != BOOLEAN:
            raise EvaluationException(f"Invalid condition: expected 'bool', got '{child[0]}'")
        while child[1]:
            return_value = self.children[1].evaluate(st)
            if return_value is not None:
                return return_value
            child = self.children[0].evaluate(st)