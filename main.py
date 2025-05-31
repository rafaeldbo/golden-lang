import json, sys

from nodes import *

NODES = {
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
    
    # "cancel": CancelOp,
    # "submit": SubmitOp,
    # "field": FormField,
    # "form_validator": FormValidator,
    # "required": FieldRequiredParam,
    # "title": FieldTitleParam,
    # "description": FieldDescriptionParam,
    # "placeholder": FieldPlaceholderParam,
    # "options": FieldOptionsParam,
    # "default": FieldDefaultParam,
    # "field_validator": FieldValidator,
    
}

def load_AST(data: dict) -> Node:
    children = [load_AST(child) for child in data.get("children", [])]
    return NODES[data["type"]](data.get("value", None), *children)
    
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <AST_file.json>")
        return
    
    filename = sys.argv[1]
    
    ASTdata = json.load(open(filename, "r"))
    AST = load_AST(ASTdata)
    AST.evaluate(SymbolTable())
    
if __name__ == "__main__":
    main()