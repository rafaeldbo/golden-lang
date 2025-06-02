from typing import Tuple

from node import Node, EvaluationException

from symbol_table import SymbolTable
from symbol_types import Symbol, DEFAULT_VALUE, STRING, BOOLEAN, LIST

class Display(Node):
    def __init__(self, void, identifier:Node, printable_expression:Node):
        super().__init__("display", identifier, printable_expression)
    
    def evaluate(self, st:SymbolTable) -> None:
        on = self.children[0].evaluate(st)
        if on.type not in ["form", "page", "field"]:
            raise EvaluationException(f"Display operation can only be performed on 'PAGE', form variable or field variable, not {on.type}")
        self.children[1].evaluate(st)
        
        
class Form(Node):
    def __init__(self, void, identifier:Node, form_block:Node):
        super().__init__("form", identifier, form_block)
    
    def evaluate(self, st:SymbolTable) -> None:
        if "root" not in st.name:
            raise EvaluationException("Form can only be defined at the root level")
        form_st = SymbolTable(st, name=f"form[{self.children[0].value}]")
        st.create(self.children[0].value, "object", Symbol("object", form_st))
        form_st.sys_create("__object_type__", STRING, Symbol(STRING, "form"))
        form_st.sys_create("__name__", STRING, Symbol(STRING, self.children[0].value))
        self.children[1].evaluate(form_st)
        
class FormField(Node):
    def __init__(self, field_type:str, identifier:Node, field_block:Node):
        super().__init__(field_type, identifier, field_block)
        
    def evaluate(self, st:SymbolTable) -> None:
        field_st = SymbolTable(st, name=f"field[{self.children[0].value}]")
        st.sys_create(self.children[0].value, "object", Symbol("object", field_st))
        field_st.sys_create("__object_type__", STRING, Symbol(STRING, "field"))
        field_st.sys_create("__name__", STRING, Symbol(STRING, self.children[0].value))
        
        value_type = self.value if self.value in DEFAULT_VALUE.keys() else "string"
        field_st.sys_create("__value__", value_type, DEFAULT_VALUE[value_type])
        
class FormValidator(Node):
    def __init__(self, void, validator_block:Node):
        super().__init__("form_validator", validator_block)
    
    def evaluate(self, st:SymbolTable) -> None:
        self.children[0].evaluate(SymbolTable(st, name="validator"))
     
class FieldValidator(Node):
    def __init__(self, void, validator_block:Node):
        super().__init__("field_validator", validator_block)
    
    def evaluate(self, st:SymbolTable) -> None:
        self.children[1].evaluate(SymbolTable(st, name="validator"))
        
class FieldRequiredParam(Node):
    def __init__(self, *void:Tuple[Node]):
        super().__init__("required")
    
    def evaluate(self, st:SymbolTable) -> None:
        st.sys_create("__required__", BOOLEAN, Symbol(BOOLEAN, True))
        
class FieldTitleParam(Node):
    def __init__(self, void, title:Node):
        super().__init__("title", title)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.sys_create("__title__", STRING, self.children[0].evaluate())
        
class FieldDescriptionParam(Node):
    def __init__(self, void, description:Node):
        super().__init__("description", description)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.sys_create("__description__", STRING, self.children[0].evaluate())
        
class FieldPlaceholderParam(Node):
    def __init__(self, placeholder:str, *void:Tuple[Node]):
        super().__init__(placeholder)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.sys_create("__placeholder__", STRING, Symbol(STRING, self.value))

class FieldOptionsParam(Node):
    def __init__(self, void, options:Node):
        super().__init__("options", options)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.sys_create("__options__", LIST, Symbol(LIST, self.children[0].evaluate(st)))
        
class FieldDefaultParam(Node):
    def __init__(self, default_value:Node, *void:Tuple[Node]):
        super().__init__("default", default_value)
    
    def evaluate(self, st:SymbolTable) -> None:
        value = self.children[0].evaluate(st)
        st.sys_create("__default__", self.value, value)
        st.setter("__value__", DEFAULT_VALUE[self.value])

class CancelOp(Node):
    def __init__(self, *void:Tuple[Node]):
        super().__init__("cancel")
    
    def evaluate(self, st:SymbolTable) -> None:
        if "validator" not in st.name:
            raise EvaluationException("Cancel operation can only be used inside a 'validator' block")
    
class SubmitOp(Node):
    def __init__(self, *void:Tuple[Node]):
        super().__init__("submit")
    
    def evaluate(self, st:SymbolTable) -> None:
        if "validator" not in st.name :
            raise EvaluationException("Submit operation can only be used inside a 'validator' block")