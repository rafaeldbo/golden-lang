from typing import List, Tuple

from .node import Node, EvaluationException
from .code_generator import Code

from .symbol_table import SymbolTable
from .symbol_types import Symbol, Date, Time, NUMBER, STRING, BOOLEAN, LIST, DATE, TIME, OBJECT


class NoOp(Node):
    def __init__(self,*void:Tuple[Node]) -> None:
        super().__init__(None)
    
    def evaluate(self, st:SymbolTable) -> None:
        pass
    
    def generate(self) -> None:
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
        
    def generate(self) -> str:
        left = self.children[0].generate()
        right = self.children[1].generate()
        
        if self.value == "equal":
            return f"({left}).equals({right})"
        elif self.value == "not_equal":
            return f"!({left}).equals({right})"
        elif self.value == "greater":
            return f"{left} > {right}"
        elif self.value == "less":
            return f"{left} < {right}"
              
        elif self.value == "plus":
            return f"({left}).add({right})"
        elif self.value == "minus":
            return f"({left}).subtract({right})"
        elif self.value == "mult":
            return f"{left} * {right}"
        elif self.value == "div":
            return f"{left} / {right}"
            
        elif self.value == "and":
            return f"{left} && {right}"
        elif self.value == "or":
            return f"{left} || {right}"

class UnOp(Node):
    def __init__(self, operation:str, unary:Node):
        super().__init__(operation, unary)
        
    def evaluate(self, st:SymbolTable) -> float:
        unary = self.children[0].evaluate(st)
        
        if unary is None:
            raise EvaluationException("Cannot evaluate unary operation with None value")
        
        elif self.value == "not":
            return Symbol(BOOLEAN, not unary)
        elif self.value == "minus":
            return -unary
        
        else:
            raise EvaluationException(f"Unknown unary operation: {self.value} with {unary}")
        
    def generate(self) -> str:
        unary = self.children[0].generate()
        if self.value == "not":
            return f"!{unary}"
        elif self.value == "minus":
            return f"-{unary}"
    
class NumberValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, float]:
        return Symbol(NUMBER, float(self.value))
    
    def generate(self) -> str:
        return str(self.value)
    
class StringValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, str]:
        return Symbol(STRING, self.value)
    
    def generate(self) -> str:
        return f'"{self.value}"'
    
class BooleanValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        if value.lower() == "true":
            bool_value = True
        elif value.lower() == "false":
            bool_value = False
        else:
            raise ValueError(f"Invalid boolean value: {value}")
        super().__init__(bool_value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, bool]:
        return Symbol(BOOLEAN, self.value)
    
    def generate(self) -> str:
        return "true" if self.value else "false"
    
class DateValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, str]:
        return Symbol(DATE, Date(self.value))
    
    def generate(self) -> str:
        return f"new DateWrapper('{self.value}')"
    
class TimeValue(Node):
    def __init__(self, value:str, *void:Tuple[Node]):
        super().__init__(value)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, str]:
        return Symbol(TIME, Time(self.value))
    
    def generate(self) -> str:
        return f"new TimeWrapper('{self.value}')"
    
class ListValue(Node):
    def __init__(self, void, *values:Tuple[Node]):
        super().__init__(LIST, *values)
    
    def evaluate(self, st:SymbolTable) -> Tuple[str, List[Symbol]]:
        return (LIST, [child.evaluate(st)[1] for child in self.children])
    
    def generate(self) -> str:
        return "[" + ", ".join(child.generate() for child in self.children) + "]"
    
class Identifier(Node):
    def __init__(self, identifier:str, *void:Tuple[Node]):
        super().__init__(identifier)
    
    def evaluate(self, st:SymbolTable) -> Symbol:
        return st.getter(self.value)
    
    def generate(self) -> str:
        return self.value

class Variable(Node):
    def __init__(self, var_type:str, identifier:Identifier, expression:Node=NoOp()):
        super().__init__(var_type, identifier, expression)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.create(self.children[0].value, self.value, self.children[1].evaluate(st))
        
    def generate(self) -> None:
        identifier = self.children[0].value
        expression = self.children[1].generate()
        if expression is not None:
            Code.append_code(f"let {identifier} = {expression};")
        else:
            Code.append_code(f"let {identifier};")
    
class Assignment(Node):
    def __init__(self, void, identifier:Identifier, expression:Node):
        super().__init__("assign", identifier, expression)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.setter(self.children[0].value, self.children[1].evaluate(st))
        
    def generate(self) -> None:
        Code.append_code(f"{self.children[0].value} = {self.children[1].generate()};")

class RootBlock(Node):
    def __init__(self, void, *statements:Tuple[Node]):
        super().__init__("root_block", *statements)
    
    def evaluate(self, st:SymbolTable) -> None:
        for statement in self.children:
            statement.evaluate(st)
            
    def generate(self) -> None:
        for statement in self.children:
            statement.generate()

class Block(Node):
    def __init__(self, void, *statements:Tuple[Node]):
        super().__init__("block", *statements)
    
    def evaluate(self, st:SymbolTable) -> None:
        for statement in self.children:
            statement.evaluate(st) 
            
    def generate(self) -> None:
        Code.append_code("{")
        Code.indent += 1
        for statement in self.children:
            statement.generate()
        Code.indent -= 1
        Code.append_code("}")
    
class IfOp(Node):
    def __init__(self, void, condition:Node, if_block:Node, else_block:Node=NoOp()):
        super().__init__("if", condition, if_block, else_block)
    
    def evaluate(self, st:SymbolTable) -> Symbol:
        condition = self.children[0].evaluate(st)
        if condition.type != BOOLEAN:
            raise EvaluationException("If condition must be a boolean value")
        self.children[1].evaluate(SymbolTable(st, "if_block"))
        self.children[2].evaluate(SymbolTable(st, "else_block"))
        
    def generate(self) -> None:
        condition = self.children[0].generate()
        
        Code.append_code(f"if ({condition})")
        self.children[1].generate()
        
        if self.children[2].value is not None:
            Code.append_code(f"else")
            self.children[2].generate()
        
    
class WhileOp(Node):
    def __init__(self, void, condition:Node, block:Node):
        super().__init__("while", condition, block)
    
    def evaluate(self, st:SymbolTable) -> Symbol:
        condition = self.children[0].evaluate(st)
        if condition.type != BOOLEAN:
            raise EvaluationException("While condition must be a boolean value")
        self.children[1].evaluate(SymbolTable(st, "while_block"))

        
    def generate(self) -> None:
        condition = self.children[0].generate()
        
        Code.append_code(f"while ({condition})")
        self.children[1].generate()
        

class Attribute(Node):
    def __init__(self, attribute_name:str, *identifiers:Tuple[Node]):
        super().__init__(attribute_name, *reversed(identifiers))
    
    def evaluate(self, st:SymbolTable) -> Symbol:
        current_st = st
        for i in range(len(self.children)):
            if self.children[i] is None:
                break
            obj = self.children[i].evaluate(current_st)
            if obj.type != "object":
                raise EvaluationException(f"Expected an object, got {obj.type}")
            current_st = obj.value
        return Symbol(OBJECT, current_st) 
    
    def generate(self) -> str:
        return f"#{'.'.join(child.generate() for child in self.children)}.{self.value}"

class AttributeAccess(Node):
    def __init__(self, void, attribute:Node):
        super().__init__("attribute_access", attribute)
    
    def evaluate(self, st:SymbolTable) -> Symbol:
        obj = self.children[0].evaluate(st)
        if obj.type != "object":
            raise EvaluationException(f"Expected an object, got {obj.type}")
        
        return obj.value.getter(f"__{self.children[0].value}__")
    
    def generate(self) -> str:
        return f"{self.children[0].generate()}.get()"
        
        
class AttributeAssignment(Node):
    def __init__(self, void, attribute:Node, value:Tuple[Node]):
        super().__init__("attribute_assignment", attribute, value)
    
    def evaluate(self, st:SymbolTable) -> None:
        obj = self.children[0].evaluate(st)
        if obj.type != "object":
            raise EvaluationException(f"Expected an object, got {obj.type}")
        value = self.children[1].evaluate(st)
        
        obj.value.setter(f"__{self.children[0].value}__", value)
        
    def generate(self) -> None:
        Code.append_code(f"{self.children[0].generate()}.set({self.children[1].generate()});")