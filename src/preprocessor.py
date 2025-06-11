from .symbol_table import SymbolTable, Symbol

class PreProcessor:
    def preprocess(st: SymbolTable) -> None:
        st.create("PAGE", "page", Symbol("page", "..."))