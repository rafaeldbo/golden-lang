from typing import List
import os, shutil, re

JS_BASE = """import {{ Form, FormField, display, DateWrapper, TimeWrapper }} from './form.js';

// Generated code for {filename}.form

{code}
"""


HTML_BASE = """ <!-- Generated HTML for {filename}.form -->
<!DOCTYPE html>
<html lang="pt-br"> 
<head>
    <meta charset="UTF-8">
    <base href="./">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/meyer-reset/2.0/reset.min.css" integrity="sha512-NmLkDIU1C/C88wi324HBc+S2kLhi08PN5GDeUVVVC/BVt/9Izdsc9SVeVfA1UZbY3sHUlDSyRXhCzHfr6hmPPw==" crossorigin="anonymous" />
    <link rel="stylesheet" href="./style.css">
</head>
<body>
    <span class="PAGE" id="PAGE-display"></span>
{body}
    <script type="module" src="./script.js"></script>
</body>
</html>  
"""


class Code:
    code_instructions:List[str] = []
    html_elements:List[str] = []
    indent = 0
    inline_code = False
    inline_code_instructions:List[str] = []
        
    def append_code(stmt: str, last_block: bool = False) -> None:
        instructions = Code.inline_code_instructions if Code.inline_code else Code.code_instructions

        if last_block:
            for i in reversed(range(len(instructions))):
                if re.fullmatch(r'\t*}', instructions[i]):
                    instructions.insert(i, "\t"*(Code.indent+1) + stmt)
                    break
        else:
            instructions.append("\t"*Code.indent + stmt)

    def append_html(element: str) -> None:
        Code.html_elements.append(element)
        
    def start_inline_code() -> None:
        Code.inline_code = True
        Code.inline_code_instructions.clear()
        
    def dump_inline_code() -> str:
        code = ""
        if Code.inline_code:
            code = Code.dump_code(Code.inline_code_instructions)
            Code.inline_code = False
            Code.inline_code_instructions.clear()
        return code
    
    def dump(filename: str, path:str="./") -> None:
        template_path = os.path.join(path, 'src', 'template')
        build_path = os.path.join(path, filename)
        os.makedirs(build_path, exist_ok=True)
        with open(os.path.join(build_path, "script.js"), 'w') as js, open(os.path.join(build_path, "index.html"), 'w') as html:
            name = filename.split("/")[-1]
            
            code = Code.dump_code(Code.code_instructions).replace("#", "")
            js.write(JS_BASE.format(filename=name, code=code))

            body = "\n".join(Code.html_elements)
            html.write(HTML_BASE.format(filename=name, body=body))
        shutil.copy(os.path.join(template_path, "style.css"), os.path.join(build_path, "style.css"))
        shutil.copy(os.path.join(template_path, "form.js"), os.path.join(build_path, "form.js"))
        print(f"Code generated successfully in: {filename}/")
        print(f"To view the form run a local server in the folder: {filename}/")
        print(f"e.g. python3 -m http.server -d {filename}/")
            
    def dump_code(code_instructions: List[str]) -> str:
        code = ""
        for i, instruction in enumerate(code_instructions[:-1]):
            next_line = code_instructions[i + 1]
            formatted_line = instruction + "\n" if instruction.endswith(";") or instruction.endswith("{") else instruction + " "
            if instruction.endswith("}") and (next_line.endswith(";") or next_line.endswith("}")):
                formatted_line += "\n"
            code += formatted_line
        code += code_instructions[-1]
        return re.sub(f' \t', ' ', code)