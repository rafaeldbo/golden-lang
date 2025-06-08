from typing import List

JS_BASE = """// Generated code for {filename}.form

{code}
"""


HTML_BASE = """ <!-- Generated HTML for {filename}.form -->
<!DOCTYPE html>
<html lang="pt-br"> 
<head>
    <meta charset="UTF-8">
    <base href="/">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
    <link rel="preconnect" href="https://fonts.gstatic.com" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/meyer-reset/2.0/reset.min.css" integrity="sha512-NmLkDIU1C/C88wi324HBc+S2kLhi08PN5GDeUVVVC/BVt/9Izdsc9SVeVfA1UZbY3sHUlDSyRXhCzHfr6hmPPw==" crossorigin="anonymous" />
    <link rel="stylesheet" href="style.css">
    <link rel="javascript" href="script.js">
</head>
<body>
{body}
</body>
</html>  
"""


class Code:
    js_instructions:List[str] = []
    html_elements:List[str] = []
    
    def js_append(stmt: str) -> None:
        Code.js_instructions.append(stmt + ";")
    
    def html_append(element: str) -> None:
        Code.html_elements.append(element)
        
    def dump(filename: str) -> None:
        with open(filename+".js", 'w') as js, open(filename+".html", 'w') as html:
            name = filename.split("/")[-1]
            code = "\n".join(Code.js_instructions)
            body = "\n".join(Code.html_elements)
            js.write(JS_BASE.format(filename=name, code=code))
            html.write(HTML_BASE.format(filename=name, body=body))