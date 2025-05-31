from abc import ABC, abstractmethod
from typing import Union, List, Tuple

from symbol_table import SymbolTable
from symbol_types import Symbol, Date, Time

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
    def evaluate(self, st:SymbolTable) -> Union[Symbol, None]:
        pass


class NoOp(Node):
    def __init__(self,*void:Tuple[Node]) -> None:
        super().__init__(None)
    
    def evaluate(self, st:SymbolTable) -> None:
        pass

    
class BinOp(Node):
    def __init__(self, operation:str, left:Node, right:Node):
        super().__init__(operation, left, right)
    
    def evaluate(self, st:SymbolTable) -> Symbol:
        left = self.children[0].evaluate(st)
        right = self.children[1].evaluate(st)
        
        if left is None or right is None:
            raise EvaluationException("Cannot evaluate binary operation with None value")
        
        elif self.value == "equal":
            return left == right
        elif self.value == "greater":
            return left > right
        elif self.value == "less":
            return left < right
              
        elif self.value == "plus":
            return left + right 
        elif self.value == "minus":
            return left - right
        elif self.value == "mult":
            return left * right
        elif self.value == "div":
            return left / right
            
        elif self.value == "and":
            return left and right
        elif self.value == "or":
            return left or right
        
        else:
            raise EvaluationException(f"Unknown binary operation: {self.value} with {left} and {right}")
    
class UnOp(Node):
    def __init__(self, operation:str, unary:Node):
        super().__init__(operation, unary)
        
    def evaluate(self, st:SymbolTable) -> float:
        unary = self.children[0].evaluate(st)
        
        if unary is None:
            raise EvaluationException("Cannot evaluate unary operation with None value")
        
        elif self.value == "not":
            return not unary
        elif self.value == "minus":
            return -unary
        
        else:
            raise EvaluationException(f"Unknown unary operation: {self.value} with {unary}")
    
class NumberValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, float]:
        return Symbol(NUMBER, float(self.value))
    
class StringValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, str]:
        return Symbol(STRING, self.value)
    
class BooleanValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, bool]:
        return Symbol(BOOLEAN, self.value.lower() == "true")
    
class DateValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, str]:
        return Symbol("date", Date(self.value))
    
class TimeValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, str]:
        return Symbol(TIME, Time(self.value))
    
class ListValue(Node):
    def __init__(self, void, values:Tuple[Node]):
        super().__init__("list", values)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, List[Symbol]]:
        return (LIST, [child.evaluate(st)[1] for child in self.children])
    
class Identifier(Node):
    def __init__(self, identifier:str, *void:Tuple[Node]):
        super().__init__(identifier)
    
    def evaluate(self, st:SymbolTable) -> Symbol:
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
        for statement in self.children:
            statement.evaluate(st)

class Display(Node):
    def __init__(self, void, identifier:Node, printable_expression:Node):
        super().__init__("display", identifier, printable_expression)
    
    def evaluate(self, st:SymbolTable) -> None:
        print(f"on {self.children[0].value}:", self.children[1].evaluate(st))
    
    
class IfOp(Node):
    def __init__(self, void, condition:Node, if_block:Node, else_block:Node=None):
        super().__init__("if", condition, if_block, else_block)
    
    def evaluate(self, st:SymbolTable) -> Symbol:
        condition = self.children[0].evaluate(st)

        if condition:
            self.children[1].evaluate(st)
        elif self.children[2] is not None:
            self.children[2].evaluate(st)
    
class WhileOp(Node):
    def __init__(self, void, condition:Node, block:Node):
        super().__init__("while", condition, block)
    
    def evaluate(self, st:SymbolTable) -> Symbol:
        condition = self.children[0].evaluate(st)
        while condition:
            self.children[1].evaluate(st)
            condition = self.children[0].evaluate(st)