%{
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    void yyerror(const char *s);
    int yylex();
    extern FILE *yyin;  // Permite leitura de arquivo no Flex

    void print(const char *msg) {
        printf("%s\n", msg);
        fflush(stdout);
    }

    // Estrutura de nó da AST
    typedef union {
        char *s_value;
        float f_value;
    } Value;

    typedef struct Node {
        char *type;
        Value value;
        struct Node **children;
        int child_count;
    } Node;

    Node *create_node(const char *type, const void *value=NULL) {
        Node *node = (Node *)malloc(sizeof(Node));
        node->type = strdup(type);
        node->children = NULL;
        node->child_count = 0;

        if (!value) {
            node->value.s_value = NULL;
        } else if (strcmp(type, "number") == 0) {
            node->value.f_value = *(float *)value;
        } else {
            node->value.s_value = strdup((char *)value);
        }

        return node;
    }

    void add_child(Node *parent, Node *child) {
        parent->children = (Node **)realloc(parent->children, sizeof(Node *) * (parent->child_count + 1));
        parent->children[parent->child_count++] = child;
    }

    void free_ast(Node *node) {
        if (!node) return;

        for (int i = 0; i < node->child_count; i++) {
            free_ast(node->children[i]);
        }
        
        if (strcmp(node->type, "number") != 0) {
            free(node->value.s_value);
        }
        free(node->type);
        free(node->children);
        free(node);
    }

    void save_ast_json(Node *node, FILE *file) {
        if (!node) return;

        fprintf(file, "{ \"type\": \"%s\"", node->type);
        if (strcmp(node->type, "number") == 0) {
            fprintf(file, ", \"value\": %.2f", node->value.f_value);
        } else if (node->value.s_value) {
            fprintf(file, ", \"value\": \"%s\"", node->value.s_value);
        }

        if (node->child_count > 0 && node->children) {
            fprintf(file, ", \"children\": [");
            for (int i = 0; i < node->child_count; i++) {
                if (node->children[i]) {
                    save_ast_json(node->children[i], file);
                }
                if (i < node->child_count - 1) fprintf(file, ", ");
            }
            fprintf(file, "]");
        }
        fprintf(file, "}");
    }

    typedef struct ScopeStack {
        Node *node;
        struct ScopeStack *next;
    } ScopeStack;

    Node *ast_root = create_node("block");  // Raiz da AST
    Node *current_node = ast_root;  // Nó atual para construção da AST
    ScopeStack *node_stack = NULL; // Pilha de escopos para gerenciar blocos

    Node *create_scope_node(const char *type, const void *value=NULL) {
        Node *node = create_node(type, value);

        ScopeStack *new_stack_entry = (ScopeStack *)malloc(sizeof(ScopeStack));
        new_stack_entry->node = current_node;
        new_stack_entry->next = node_stack;
        node_stack = new_stack_entry;

        current_node = node;
        return node;
    }

    void exit_scope() {
        if (node_stack) {
            ScopeStack *old_stack_entry = node_stack;
            current_node = node_stack->node;
            node_stack = node_stack->next;
            free(old_stack_entry);
        } else {
            current_node = ast_root;
        }
    }
%}

%define parse.error verbose  // Mensagens de erro detalhadas

%locations

%union {
    float number;
    char* string;
    int boolean;
    struct Node* node; 
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

%type <node> program block start_block
%type <node> else_clause
%type <node> boolean_expression boolean_factor boolean_term expression term factor
%type <node> form_block field_block field_params field_type 

%start program

%%

program:
    statement_list { print("root"); }
    ;

start_block:
    OPEN_BRK NEWLINE { $$ = create_scope_node("block"); }
    ;

block:
    start_block statement_list CLOSE_BRK { exit_scope(); $$ = $1; }
    ;

statement_list:
    /* vazio */
    | NEWLINE statement_list
    | statement NEWLINE statement_list
    | statement YYEOF
    ;


statement:
      IF boolean_expression THEN block { Node *node = create_node("if"); add_child(node, $2); add_child(node, $4); add_child(current_node, node); }
    | IF boolean_expression THEN block else_clause { Node *node = create_node("if"); add_child(node, $2); add_child(node, $4); add_child(node, $5); add_child(current_node, node); }
    | WHILE boolean_expression REPEAT block { Node *node = create_node("while"); add_child(node, $2); add_child(node, $4); add_child(current_node, node); }
    | type IDENTIFIER ASSIGN boolean_expression { Node *node = create_node("variable", $1); add_child(node, create_node("indentifier", $2)); add_child(node, $4); add_child(current_node, node); }
    | type IDENTIFIER { Node *node = create_node("variable", $1); add_child(node, create_node("identifier", $2)); add_child(current_node, node); }
    | IDENTIFIER ASSIGN boolean_expression { Node *node = create_node("assignment"); add_child(node, create_node("identifier", $1)); add_child(node, $3); add_child(current_node, node); }
    | FORM IDENTIFIER OPEN_BRK form_statement_list CLOSE_BRK // { Node *node = create_node("variable", "form"); add_child(node, create_node("identifier", $2)); add_child(node, $4); add_child(current_node, node); }
    | ON OPEN_SQR IDENTIFIER CLOSE_SQR DISPLAY OPEN_PAR boolean_expression CLOSE_PAR { Node *node = create_node("display"); add_child(node, create_node("identifier", $3)); add_child(node, $7); add_child(current_node, node); }
    | CANCEL { Node *node = create_node("cancel"); add_child(current_node, node); }
    | SUBMIT { Node *node = create_node("submit"); add_child(current_node, node); }
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

form_block:
    OPEN_BRK NEWLINE form_statement_list CLOSE_BRK { current_node = create_node("form_block"); $$ = current_node; }
    ;

field_block:
    OPEN_BRK NEWLINE field_params CLOSE_BRK { current_node = create_node("field_block"); $$ = current_node; }
    ;

form_statement_list:
    /* vazio */
    | NEWLINE form_statement_list
    | FIELD IDENTIFIER field_type OPEN_BRK NEWLINE field_params CLOSE_BRK NEWLINE form_statement_list // { $$ = create_node("form_field"); add_child($$, create_node("identifier", $2)); add_child($$, $5); }
    | VALIDATOR block NEWLINE form_statement_list // { $$ = create_node("form_validator"); add_child($$, $2); }
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
      NUMBER { $$ = create_node("number", &($1)); }
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