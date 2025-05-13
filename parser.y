%{
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    void yyerror(const char *s);
    int yylex();
    extern FILE *yyin;  // Permite leitura de arquivo no Flex
%}

%define parse.error verbose  // Mensagens de erro detalhadas

%locations

%union {
    int number;
    char* string;
    int boolean;
}

%token NUMBER STRING TIME DATE IDENTIFIER BOOLEAN
%token NUMBER_TYPE STRING_TYPE BOOLEAN_TYPE TIME_TYPE DATE_TYPE
%token PLUS MINUS MULT DIV ASSIGN
%token OPEN_PAR CLOSE_PAR OPEN_BRK CLOSE_BRK OPEN_SQR CLOSE_SQR
%token DOT COMMA SEMICOLON
%token NOT AND OR
%token EQUAL GREATER LESS
%token IF THEN ELSE WHILE REPEAT NEW
%token FIELD FORM ON DISPLAY CANCEL SUBMIT
%token REQUIRED TITLE DESCRIPTION PLACEHOLDER DEFAULT SELECT OPTIONS VALIDATOR
%token NEWLINE

%type <number> NUMBER
%type <string> STRING TIME DATE IDENTIFIER

%start program

%%

program:
    statement_list
    ;

block:
    OPEN_BRK NEWLINE statement_list CLOSE_BRK
    ;

statement_list:
    /* vazio */
    | NEWLINE statement_list
    | statement NEWLINE statement_list 
    | statement YYEOF
    ;

statement:
      IF boolean_expression THEN block
    | IF boolean_expression THEN block else_clause
    | WHILE boolean_expression REPEAT block
    | type IDENTIFIER ASSIGN boolean_expression
    | type IDENTIFIER
    | IDENTIFIER ASSIGN boolean_expression
    | FORM IDENTIFIER OPEN_BRK form_statement_list CLOSE_BRK
    | ON OPEN_SQR IDENTIFIER CLOSE_SQR DISPLAY OPEN_PAR boolean_expression CLOSE_PAR
    | CANCEL
    | SUBMIT
    ;

else_clause:
      ELSE IF boolean_expression THEN block
    | ELSE IF boolean_expression THEN block else_clause
    | ELSE block
    ;

type:
      NUMBER_TYPE
    | STRING_TYPE
    | BOOLEAN_TYPE
    | TIME_TYPE
    | DATE_TYPE
    ;

form_statement_list:
    /* vazio */
    | NEWLINE form_statement_list
    | FIELD IDENTIFIER field_type OPEN_BRK NEWLINE field_params CLOSE_BRK NEWLINE form_statement_list
    | VALIDATOR block NEWLINE form_statement_list
    ;

field_params:
    /* vazio */
    | NEWLINE field_params
    | REQUIRED field_params
    | TITLE ASSIGN boolean_expression NEWLINE field_params
    | DESCRIPTION ASSIGN boolean_expression NEWLINE field_params
    | PLACEHOLDER ASSIGN boolean_expression NEWLINE field_params
    | DEFAULT ASSIGN boolean_expression NEWLINE field_params
    | OPTIONS ASSIGN list NEWLINE field_params
    | VALIDATOR block NEWLINE field_params
    ;

field_type:
      NUMBER_TYPE
    | STRING_TYPE
    | TIME_TYPE
    | DATE_TYPE
    | SELECT
    ;

list: 
    OPEN_SQR NEWLINE list_items CLOSE_SQR
    ;

list_items:
    /* vazio */
    | NEWLINE list_items
    | boolean_expression COMMA list_items
    | boolean_expression NEWLINE
    ;


boolean_expression:
      boolean_term
    | boolean_term OR boolean_term
    ;

boolean_term:
      boolean_factor
    | boolean_factor AND boolean_factor
    ;

boolean_factor:
      expression
    | expression EQUAL expression
    | expression GREATER expression
    | expression LESS expression
    ;

expression:
      term
    | term PLUS term
    | term MINUS term
    ;

term:
      factor
    | factor MULT factor
    | factor DIV factor
    ;

factor:
      NUMBER
    | STRING
    | BOOLEAN
    | DATE
    | TIME
    | IDENTIFIER
    | MINUS factor
    | NOT factor
    | OPEN_PAR boolean_expression CLOSE_PAR
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "[!] %s\n", s);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <arquivo_entrada>\n", argv[0]);
        return 1;
    }

    FILE *arquivo = fopen(argv[1], "r");
    if (!arquivo) {
        fprintf(stderr, "Erro ao abrir o arquivo: %s\n", argv[1]);
        return 1;
    }

    // Define a entrada do Flex para o arquivo
    yyin = arquivo;

    // Executa o parser
    if (yyparse() == 0)
        printf("Análise sintática concluída com sucesso.\n");


    fclose(arquivo);
    return 0;
}