# Golden-Lang

Repositório para o projeto final da disciplina `Lógica da Computação` Insper 2025.1.

O projeto consiste em uma Linguagem de programação voltada para a construção de formulários. O objetivo é facilitar a criação de formulários complexos que possui diferentes campos, validação de entradas e estruturas complexas. 

A linguagem será estruturada com uma sintaxe simples, mas completa o suficiente para permitir a criação de formulários complexos. A linguagem compiará diretamente para HTML+JS, permitindo que os formulários sejam utilizados em qualquer navegador moderno.

## Utilização
Primeiro é necessário compilar o analisador sintático `Flex e Bison` utilizando os comando:
```bash
# Executando na raiz do respositório
flex src/flex_bison/lexer.l && mv lex.yy.c src/flex_bison/lex.yy.c
bison -d src/flex_bison/parser.y -o src/flex_bison/parser.tab.c        
g++ src/flex_bison/parser.tab.c src/flex_bison/lex.yy.c -o src/flex_bison/parser
```
ou
```bash
# Executando na pasta src/flex_bison
flex lexer.l
bison -d parser.y
g++ parser.tab.c lex.yy.c -o parser
```
Em seguida, já é possível utilizar o compilador da `golden-lang` com o comando:
```bash
python3 main.py <filename.form>
```

**OBS.:** um código de teste está disponível em [exemple.form](./exemple.form)

## EBNF
```ebnf
(* Estruturas de Básicas *)
DIGIT   = ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 ) ;
LETTER  = ( a | ... | z | A | ... | Z ) ;
SYMBOL  = ( "." | "," | ";" | ":" | "!" | "?" | ... ) ;

(* Estuturas dos Tipos *)
NUMBER  = DIGIT, { DIGIT }, [ "." , DIGIT, { DIGIT } ] ;
STRING  = '"', { (LETTER | DIGIT | SYMBOL | " " | "\n" ) }, '"' ;
BOOLEAN = ( "true" | "false" ) ;

HOUR    = ( ( 0 | 1 ), DIGIT ) | ( 2, ( 0 | ... | 3 ) ) ;
MINUTE  = ( 0 | ... | 5 ), ( 0 | ... | 9 ) ;
TIME    = '"', HOUR, ":", MINUTE, '"' ;

YEAR    = DIGIT, DIGIT, DIGIT, DIGIT ;
MONTH   = ( 0, ( 1 | ... | 9 ) ) | ( 1, ( 0 | 1 | 2 ) ) ;
DAY     = ( ( 0 | 1 | 2 ), DIGIT ) | ( 3, ( 0 | 1 ) ) ;
DATE    = '"', YEAR, "-", MONTH, "-", DAY, '"';

(* Expressões *)
BOOLEAN_EXPRESSION = BOOLEAN_TERM, "or", BOOLEAN_EXPRESSION ;
BOOLEAN_TERM       = BOOLEAN_FACTOR, "and", BOOLEAN_TERM ;
BOOLEAN_FACTOR     = EXPRESSION, ( "==" | "!="  | ">" | "<" | ">=" | "<="), BOOLEAN_FACTOR ;

EXPRESSION = TERM, { ("+" | "-"), EXPRESSION } ;
TERM       = FACTOR, { ("*" | "/"), TERM } ;
FACTOR     = (
    ( ( "-" | "not" ), FACTOR ) | 
    NUMBER | STRING | BOOLEAN | DATE | TIME |
    ( "(", EXPRESSION, ")" ) |
    IDENTIFIER |
    ATTRIBUTE
) ;

(* Estuturas de Variáveis *)
TYPE       = ( "String" | "Number" | "Boolean" | "Date" | "Hour" ) ;
IDENTIFIER = LETTER, { LETTER | DIGIT | "_" } ;
VARIABLE   = TYPE, IDENTIFIER, ":", TYPE, [ "=", BOOLEAN_EXPRESSION ] ;
ASSIGNMENT = ( IDENTIFIER | ATTRIBUTE ), "=", EXPRESSION ;
ATTRIBUTE  = IDENTIFIER, ".", { IDENTIFIER, "." }, FIELD_ATTRIBUTE ;

FIELD_ATTRIBUTE = (
    "value" |
    "required" |
    "title" |
    "description" |
    "placeholder" |
    "default" |
    "options"
) ;

(* Estruturas de Código *)
CODE_STATEMENT = ( λ | VARIABLE | ASSIGNMENT | IF | LOOP | "cancel" ), "\n" ;
CODE_BLOCK     = "{", "\n", { CODE_STATEMENT }, "}" ;

IF      = "if", BOOLEAN_EXPRESSION, "then", CODE_BLOCK, ELSE_IF ;
ELSE_IF = { "else", "if", BOOLEAN_EXPRESSION, CODE_BLOCK }, [ "else", CODE_BLOCK ]
LOOP    = "while", BOOLEAN_EXPRESSION, "repeat", CODE_BLOCK ;

(* Funções Básicas *)	
DISPLAY = "on", "[", IDENTIFIER, "]", "display", "(", BOOLEAN_EXPRESSION, ")" ;

(* Estruturas de Formulário *)
FIELD_TYPE      = ( TYPE | "Select" ) ;
FIELD           = "Field", IDENTIFIER, FIELD_TYPE, FIELD_BLOCK ;
FIELD_BLOCK     = "{", "\n" { FIELD_STATEMENT }, "}", "\n" ;
FIELD_STATEMENT = ( 
    "required" | 
    ( "placeholder", "=", BOOLEAN_EXPRESSION ) | 
    ( "title", "=", "BOOLEAN_EXPRESSION" ) |
    ( "description", "=", BOOLEAN_EXPRESSION ) | 
    ( "default", "=", BOOLEAN_EXPRESSION ) | 
    ( "options", "=", "[", { BOOLEAN_EXPRESSION }, "]" ) |
    ( "onChange", CODE_BLOCK )  
), "\n" ;

FORM           = "Form", IDENTIFIER , FORM_BLOCK ;
FORM_BLOCK     = "{", "\n" { FORM_STATEMENT }, "}", "\n" ;
FORM_STATEMENT = ( FIELD | ( "onSubmit", CODE_BLOCK ) ) ;

(* Bloco Inicial *)
ROOT_BLOCK = { ( CODE_STATEMENT | FORM ) } ;
```