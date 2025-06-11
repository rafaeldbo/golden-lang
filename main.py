import sys, os, subprocess

from src.ast_read import read_AST
from src.preprocessor import PreProcessor
from src.node import SymbolTable
from src.code_generator import Code

PATH = os.path.join(os.path.dirname(__file__))
    
def run_parser(filename: str, path: str = "./") -> None:
    """Executa parser flex+bison para gerar o AST a partir do arquivo .form."""
    try:
        result = subprocess.run([os.path.join(path, "src", "flex_bison", "parser"), filename], capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erro ao executar o comando:")
        print(e.stderr)
    
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <exemple.form>")
        return
    
    
    form_filename = sys.argv[1]
    run_parser(form_filename, PATH)
    filename = os.path.splitext(form_filename)[0]
    ast_filename = filename+".json"
    
    AST = read_AST(ast_filename)
    st = SymbolTable(name="root")
    PreProcessor.preprocess(st)
    AST.evaluate(st)
    # print(st)
    AST.generate()
    Code.dump(filename)
    
if __name__ == "__main__":
    main()