from typing import List, Tuple
import re

from code_generator import Code
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
        
    def generate(self) -> None:
        Code.append_code(f"display('{self.children[0].value}', {self.children[1].generate()});")
        
        
class ObjectBlock(Node):
    def __init__(self, void, *statements:Tuple[Node]):
        super().__init__("object_block", *statements)
    
    def evaluate(self, st:SymbolTable) -> None:
        for statement in self.children:
            statement.evaluate(st)
            
    def generate(self) -> List[str]:
        return [statement.generate() for statement in self.children]
        
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
        Node.late_evaluate()
        
    def generate(self) -> None:
        form_name = self.children[0].value
        Code.append_html(f'<form id="{form_name}" name="{form_name}">')
        Code.append_html(f'<h1 id="{form_name}-title"></h1>')
        onSubmit = "onSubmit: () => {{}}"
        childs = self.children[1].generate()
        for child in childs:
            if child.startswith("onSubmit: "):
                onSubmit = child
                childs.remove(child)
                break
        fields = ",\n".join(childs)
        form_statement = f"const {form_name} = new Form('{form_name}', {{fields: [\n{fields}], {onSubmit}}});"
        form_statement = re.sub(fr"#({form_name}\.)?", lambda m: "" if m.group(1) else f"{form_name}.", form_statement)
        Code.append_code(form_statement)
        Code.append_html(f'<button type="submit" id="{form_name}-submit">Submit</button>')
        Code.append_html("</form>")
        
class FormField(Node):
    def __init__(self, field_type:str, identifier:Node, field_block:Node):
        super().__init__(field_type, identifier, field_block)
        
    def evaluate(self, st:SymbolTable) -> None:
        field_name = self.children[0].value
        field_st = SymbolTable(st, name=f"field[{field_name}]")
        st.sys_create(field_name, "object", Symbol("object", field_st))
        field_st.sys_create("__object_type__", STRING, Symbol(STRING, "field"))
        field_st.sys_create("__name__", STRING, Symbol(STRING, field_name))
        
        value_type = self.value if self.value in DEFAULT_VALUE.keys() else "string"
        field_st.sys_create("__type__", STRING, Symbol(STRING, self.value.lower() if self.value != "String" else "text"))
        field_st.sys_create("__value__", value_type, DEFAULT_VALUE[value_type])
        field_st.sys_create("__required__", BOOLEAN, Symbol(BOOLEAN, False))
        field_st.sys_create("__title__", STRING, Symbol(STRING, field_name))
        field_st.sys_create("__description__", STRING, Symbol(STRING, ""))
        if self.value == "Select":
            field_st.sys_create("__options__", LIST, Symbol(LIST, []))
        else:
            field_st.sys_create("__placeholder__", STRING, Symbol(STRING, ""))
        
    def generate(self) -> None:
        field_name = self.children[0].value
        field_type = self.value.lower() if self.value != "String" else "text"
        
        Code.append_html(f'<section class="field" id="{field_name}-section">')
        Code.append_html(f'<label for="{field_name}" id="{field_name}-title">{field_name}</label>')
        Code.append_html(f'<p id="{field_name}-description"></p>')
        if field_type == "select":
            Code.append_html(f'<select id="{field_name}" name="{field_name}"></select>')
        else:
            Code.append_html(f'<input type="{field_type}" id="{field_name}" name="{field_name}" />')
        Code.append_html(f'<span id="{field_name}-display"></span>')
        Code.append_html('</section>')
        
        return f"new FormField('{field_name}', '{field_type}', {{{', '.join(self.children[1].generate())}}})"
        
class FormOnSubmit(Node):
    def __init__(self, void, onSubmit_block:Node):
        super().__init__("form_onSubmit", onSubmit_block)
    
    def evaluate(self, st:SymbolTable) -> None:
        Node.await_evaluate(self, st)
        
    def late_evaluate(self, st:SymbolTable) -> None:
        self.children[0].evaluate(SymbolTable(st, name="onSubmit"))
        
    def generate(self) -> str:
        Code.start_inline_code()
        Code.append_code(f"() => ")
        self.children[0].generate()
        Code.append_code("return true;", last_block=True)
        onSubmit = Code.dump_inline_code()
        return f"onSubmit: {onSubmit}"
     
class FieldOnChange(Node):
    def __init__(self, void, onChange_block:Node):
        super().__init__("field_onChange", onChange_block)
    
    def evaluate(self, st:SymbolTable) -> None:
        Node.await_evaluate(self, st)
        
    def late_evaluate(self, st:SymbolTable) -> None:
        self.children[0].evaluate(SymbolTable(st, name="onChange"))
        
    def generate(self) -> str:
        Code.start_inline_code()
        Code.append_code(f"() => ")
        self.children[0].generate()
        Code.append_code("return true;", last_block=True)
        onChange = Code.dump_inline_code()
        return f"onChange: {onChange}"
        
class FieldRequiredParam(Node):
    def __init__(self, *void:Tuple[Node]):
        super().__init__("required")
    
    def evaluate(self, st:SymbolTable) -> None:
        st.setter("__required__", BOOLEAN, Symbol(BOOLEAN, True))
        
    def generate(self) -> str:
        return "required: true"
        
class FieldTitleParam(Node):
    def __init__(self, void, title:Node):
        super().__init__("title", title)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.sys_create("__title__", STRING, self.children[0].evaluate(st))
    
    def generate(self) -> str:
        title = self.children[0].generate()
        return f"title: {title}"
        
class FieldDescriptionParam(Node):
    def __init__(self, void, description:Node):
        super().__init__("description", description)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.setter("__description__", self.children[0].evaluate(st))
        
    def generate(self) -> str:
        description = self.children[0].generate()
        return f"description: {description}"
        
class FieldPlaceholderParam(Node):
    def __init__(self, void:str, placeholder:Node):
        super().__init__("placeholder", placeholder)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.setter("__placeholder__", self.children[0].evaluate(st))

    def generate(self) -> str:
        placeholder = self.children[0].generate()
        return f'placeholder: {placeholder}'

class FieldOptionsParam(Node):
    def __init__(self, void, options:Node):
        super().__init__("options", options)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.setter("__options__", self.children[0].evaluate(st))
        
    def generate(self) -> str:
        options = self.children[0].generate()
        return f'options: {options}'
        
class FieldDefaultParam(Node):
    def __init__(self, void, default_value:Node):
        super().__init__("default", default_value)
    
    def evaluate(self, st:SymbolTable) -> None:
        st.setter("__value__", self.children[0].evaluate(st))
        
    def generate(self) -> str:
        default_value = self.children[0].generate()
        return f'defaultValue: {default_value}'

class CancelOp(Node):
    def __init__(self, *void:Tuple[Node]):
        super().__init__("cancel")
    
    def evaluate(self, st:SymbolTable) -> None:
        current_st = st
        while current_st.parent is not None:
            if current_st.name.startswith("onChange") or current_st.name.startswith("onSubmit"):
                return
            current_st = current_st.parent
        raise EvaluationException("Cancel operation can only be used inside a 'onChange' block or 'onSubmit' block")
        
    def generate(self) -> None:
        Code.append_code("return false;")