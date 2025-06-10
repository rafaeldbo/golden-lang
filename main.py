import json, sys

from preprocessor import PreProcessor
from node import Node, SymbolTable
from code_generator import Code
from nodes_basic import RootBlock, Block, Identifier, Variable, Assignment, BinOp, UnOp, IfOp, WhileOp
from nodes_basic import NumberValue, StringValue, BooleanValue, DateValue, TimeValue, ListValue, Attribute, AttributeAccess, AttributeAssignment
from nodes_form import Display, ObjectBlock, Form, FormField, FormOnSubmit, FieldOnChange
from nodes_form import FieldRequiredParam, FieldTitleParam, FieldDescriptionParam, FieldPlaceholderParam, FieldOptionsParam, FieldDefaultParam, CancelOp


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
    AST.generate()
    Code.dump("teste")
    
if __name__ == "__main__":
    main()