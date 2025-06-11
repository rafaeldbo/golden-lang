import sys, os, json

from .node import Node
from .nodes_basic import RootBlock, Block, Identifier, Variable, Assignment, BinOp, UnOp, IfOp, WhileOp
from .nodes_basic import NumberValue, StringValue, BooleanValue, DateValue, TimeValue, ListValue, Attribute, AttributeAccess, AttributeAssignment
from .nodes_form import Display, ObjectBlock, Form, FormField, FormOnSubmit, FieldOnChange
from .nodes_form import FieldRequiredParam, FieldTitleParam, FieldDescriptionParam, FieldPlaceholderParam, FieldOptionsParam, FieldDefaultParam, CancelOp

NODES = {
    "root": RootBlock,
    "block": Block,
    "identifier": Identifier,
    "variable": Variable,
    "assignment": Assignment,
    "bin_op": BinOp,
    "un_op": UnOp,
    "if": IfOp,
    "while": WhileOp,
    "display": Display,
    
    "number": NumberValue,
    "string": StringValue,
    "boolean": BooleanValue,
    "date": DateValue,
    "time": TimeValue,
    "list": ListValue,
    
    "attribute": Attribute,
    "attribute_access": AttributeAccess,
    "attribute_assignment": AttributeAssignment,
    
    "object": ObjectBlock,
    "form": Form,
    "field": FormField,
    "form_onSubmit": FormOnSubmit,
    "required": FieldRequiredParam,
    "title": FieldTitleParam,
    "description": FieldDescriptionParam,
    "placeholder": FieldPlaceholderParam,
    "options": FieldOptionsParam,
    "default": FieldDefaultParam,
    "field_onChange": FieldOnChange,
    "cancel": CancelOp,
}

def load_AST(data: dict) -> Node:
    children = [load_AST(child) for child in data.get("children", [])]
    try:
        node = NODES[data["type"]]
        return node(data.get("value", None), *children)
    except Exception as e:
        print(f"Error loading node: {node} with data: {data}")
        print(f"report this issue to the developers")
        sys.exit(1)
    
def read_AST(filename:str, path:str="./") -> Node:
    ast_filepath = os.path.join(path, filename)
    try:
        with open(ast_filepath, "r") as file:
            ASTdata = json.load(file)    
    except FileNotFoundError:
        print(f"Error: File {ast_filepath} not found.")
        sys.exit(1)
    AST = load_AST(ASTdata)
    print(f"AST loaded successfully from {ast_filepath}")
    os.remove(ast_filepath)
    return AST