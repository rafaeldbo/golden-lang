%{
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    void yyerror(const char *s);
    int yylex();
    extern FILE *yyin;  // Permite leitura de arquivo no Flex

    // Estrutura de nó da AST
    typedef struct Node {
        char *type;
        char *value;
        struct Node **children;
        int child_count;
    } Node;

    Node *create_node(const char *type, const char *value=NULL) {
        Node *node = (Node *)malloc(sizeof(Node));
        node->type = strdup(type);
        node->value = value ? strdup(value) : NULL;
        node->children = NULL;
        node->child_count = 0;
        return node;
    }

    void add_child(Node *parent, Node *child) {
        parent->children = (Node**)realloc(parent->children, sizeof(Node*) * (parent->child_count + 1));
        parent->children[parent->child_count++] = child;
    }

    void free_ast(Node *node) {
        if (!node) return;

        for (int i = 0; i < node->child_count; i++) {
            free_ast(node->children[i]);
        }
        free(node);
    }

    void save_ast_json(Node *node, FILE *file) {
        if (!node) {
            fprintf(file, "null");
            return;
        }

        fprintf(file, "{ \"type\": \"%s\"", node->type);
        if (node->value) fprintf(file, ", \"value\": \"%s\"", node->value);

        if (node->child_count > 0 && node->children) {
            fprintf(file, ", \"children\": [");
            for (int i = 0; i < node->child_count; i++) {
                if (node->children[i]) {
                    fflush(file);
                    save_ast_json(node->children[i], file);
                } else {
                    fprintf(file, "null");
                }
                if (i < node->child_count - 1) fprintf(file, ", ");
            }
            fprintf(file, "]");
        }
        fprintf(file, "}");
    }

    void print(const char *msg) {
        printf("%s\n", msg);
        fflush(stdout);
    }


    Node *ast_root = create_node("block");  // Raiz da AST
    Node *current_node = ast_root;  // Nó atual para construção da AST
%}

%define parse.error verbose  // Mensagens de erro detalhadas

%locations

%union {
    float number;
    char* string;
    int boolean;
    struct Node* node;  // Adicionando Node* ao union
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
%type <string> STRING TIME DATE IDENTIFIER type
%type <boolean> BOOLEAN

%type <node> program block statement
%type <node> else_clause
%type <node> boolean_expression boolean_factor boolean_term expression term factor

%start program

%%

program:
    statement_list { printf("root\n"); fflush(stdout); }
    ;

block:
    OPEN_BRK NEWLINE statement_list CLOSE_BRK { printf("new block\n"); fflush(stdout); current_node = create_node("block"); $$ = current_node; }
    ;

statement_list:
    /* vazio */
    | NEWLINE statement_list
    | statement NEWLINE statement_list { printf("new statement in statement_list\n"); fflush(stdout); add_child(current_node, $1); }
    | statement YYEOF { add_child(current_node, $1); }
    ;


statement:
      IF boolean_expression THEN block { $$ = create_node("if"); add_child($$, $2); add_child($$, $4); }
    | IF boolean_expression THEN block else_clause { $$ = create_node("if"); add_child($$, $2); add_child($$, $4); add_child($$, $5); }
    | WHILE boolean_expression REPEAT block { $$ = create_node("while"); add_child($$, $2); add_child($$, $4); }
    | type IDENTIFIER ASSIGN boolean_expression { $$ = create_node("variable", $1); add_child($$, create_node("indentifier", $2)); add_child($$, $4); }
    | type IDENTIFIER { $$ = create_node("variable", $1); add_child($$, create_node("identifier", $2));}
    | IDENTIFIER ASSIGN boolean_expression { $$ = create_node("assignment"); add_child($$, create_node("identifier", $1)); add_child($$, $3); }
    | FORM IDENTIFIER OPEN_BRK form_statement_list CLOSE_BRK // { $$ = create_node("variable", "form"); add_child($$, create_node("identifier", $2)); add_child($$, $4); }
    | ON OPEN_SQR IDENTIFIER CLOSE_SQR DISPLAY OPEN_PAR boolean_expression CLOSE_PAR { $$ = create_node("display"); add_child($$, create_node("identifier", $3)); add_child($$, $7); }
    | CANCEL { $$ = create_node("cancel"); }
    | SUBMIT { $$ = create_node("submit"); }
    ;

else_clause:
      ELSE IF boolean_expression THEN block { $$ = create_node("if"); add_child($$, $3); add_child($$, $5); }
    | ELSE IF boolean_expression THEN block else_clause { $$ = create_node("if"); add_child($$, $3); add_child($$, $5); add_child($$, $6); }
    | ELSE block { $$ = $2;}
    ;

type:
      NUMBER_TYPE { $$ = strdup("number"); }
    | STRING_TYPE { $$ = strdup("string"); }
    | BOOLEAN_TYPE { $$ = strdup("boolean"); }
    | TIME_TYPE { $$ = strdup("time"); }
    | DATE_TYPE { $$ = strdup("date"); }
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
      boolean_term { $$ = $1; }
    | boolean_term OR boolean_term { $$ = create_node("bin_op", "or"); add_child($$, $1); add_child($$, $3); }
    ;

boolean_term:
      boolean_factor { $$ = $1; }
    | boolean_factor AND boolean_factor { $$ = create_node("bin_op", "and"); add_child($$, $1); add_child($$, $3); }
    ;

boolean_factor:
      expression { $$ = $1; }
    | expression EQUAL expression { $$ = create_node("bin_op", "equal"); add_child($$, $1); add_child($$, $3); }
    | expression GREATER expression { $$ = create_node("bin_op", "greater"); add_child($$, $1); add_child($$, $3); }
    | expression LESS expression { $$ = create_node("bin_op", "less"); add_child($$, $1); add_child($$, $3); }
    ;

expression:
      term { $$ = $1; }
    | term PLUS term  { $$ = create_node("bin_op", "plus"); add_child($$, $1); add_child($$, $3); }
    | term MINUS term { $$ = create_node("bin_op", "minus"); add_child($$, $1); add_child($$, $3); }
    ;

term:
      factor { $$ = $1; }
    | factor MULT factor { $$ = create_node("bin_op", "mult"); add_child($$, $1); add_child($$, $3); }
    | factor DIV factor { $$ = create_node("bin_op", "div"); add_child($$, $1); add_child($$, $3); }
    ;

factor:
      NUMBER { char n_value[24]; sprintf(n_value, "%.8f", $1); $$ = create_node("number", n_value); }
    | STRING { $$ = create_node("string", $1); }
    | BOOLEAN { $$ = create_node("boolean", $1 ? "true" : "false"); }
    | DATE { $$ = create_node("date", $1); }
    | TIME { $$ = create_node("time", $1); }
    | IDENTIFIER { $$ = create_node("identifier", $1); }
    | MINUS factor { $$ = create_node("un_op", "minus"); add_child($$, $2); }
    | NOT factor { $$ = create_node("un_op", "not"); add_child($$, $2); }
    | OPEN_PAR boolean_expression CLOSE_PAR { $$ = $2; }
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

    char source_filename[256];
    strcpy(source_filename, argv[1]);
    FILE *source_file = fopen(source_filename, "r");
    if (!source_file) {
        fprintf(stderr, "Erro ao abrir o arquivo: %s\n", source_filename);
        return 1;
    }

    char output_filename[256];
    strcpy(output_filename, source_filename);
    char *dot = strrchr(output_filename, '.');
    (dot) ? strcpy(dot, ".json") : strcat(output_filename, ".json");
    FILE *output_file = fopen(output_filename, "w");
    if (!output_file) {
        perror("Erro ao abrir/criar o arquivo de saida da AST");
        return 1;
    }

    yyin = source_file;

    // Executa o parser
    if (yyparse() == 0) {
        printf("Análise sintática concluída com sucesso.\n");
        save_ast_json(ast_root, output_file);  // Imprime a AST gerada

        // free_ast(ast_root);  // Libera a memória da AST
    }

    fclose(source_file);
    fclose(output_file);
    return 0;
}