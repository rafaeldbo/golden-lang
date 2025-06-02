import json, sys

from preprocessor import PreProcessor
from node import Node, SymbolTable
from nodes_basic import RootBlock, Block, Identifier, Variable, Assignment, BinOp, UnOp, IfOp, WhileOp
from nodes_basic import NumberValue, StringValue, BooleanValue, DateValue, TimeValue, ListValue, Attribute, AttributeAccess, AttributeAssignment
from nodes_form import Display, Form, FormField, FormValidator, FieldValidator
from nodes_form import FieldRequiredParam, FieldTitleParam, FieldDescriptionParam, FieldPlaceholderParam, FieldOptionsParam, FieldDefaultParam, CancelOp, SubmitOp


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
    
    "form": Form,
    "field": FormField,
    "form_validator": FormValidator,
    "required": FieldRequiredParam,
    "title": FieldTitleParam,
    "description": FieldDescriptionParam,
    "placeholder": FieldPlaceholderParam,
    "options": FieldOptionsParam,
    "default": FieldDefaultParam,
    "field_validator": FieldValidator,
    "cancel": CancelOp,
    "submit": SubmitOp,
    
}

def load_AST(data: dict) -> Node:
    children = [load_AST(child) for child in data.get("children", [])]
    try:
        node = NODES[data["type"]]
        return node(data.get("value", None), *children)
    except Exception as e:
        print(node)
        print(data)
        raise e

    
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <AST_file.json>")
        return
    
    filename = sys.argv[1]
    
    ASTdata = json.load(open(filename, "r"))
    AST = load_AST(ASTdata)
    st = SymbolTable(name="root")
    PreProcessor.preprocess(st)
    AST.evaluate(st)
    # print(st)
if __name__ == "__main__":
    main()