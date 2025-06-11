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
            fprintf(file, ", \"value\": %.8g", node->value.f_value);
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

    Node *root = create_node("root");  // Raiz da AST
    Node *current_scope = root;  // scopo atual para colocar os nós da AST
    ScopeStack *scope_stack = NULL; // Pilha de escopos para gerenciar blocos

    Node *create_scope_node(const char *type, const void *value=NULL) {
        Node *node = create_node(type, value);

        ScopeStack *new_stack_entry = (ScopeStack *)malloc(sizeof(ScopeStack));
        new_stack_entry->node = current_scope;
        new_stack_entry->next = scope_stack;
        scope_stack = new_stack_entry;

        current_scope = node;
        return node;
    }

    void exit_scope() {
        if (scope_stack) {
            ScopeStack *old_stack_entry = scope_stack;
            current_scope = scope_stack->node;
            scope_stack = scope_stack->next;
            free(old_stack_entry);
        } else {
            current_scope = root;
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
%token EQUAL NOT_EQUAL GREATER LESS
%token IF THEN ELSE WHILE REPEAT NEW
%token FIELD FORM ON DISPLAY CANCEL
%token VALUE REQUIRED TITLE DESCRIPTION PLACEHOLDER DEFAULT SELECT OPTIONS ONCHANGE ONSUBMIT
%token NEWLINE

%type <number> NUMBER
%type <string> STRING TIME DATE IDENTIFIER 
%type <boolean> BOOLEAN

%type <string> type field_type field_attribute

%type <node> start_block block start_object form_block field_block 
%type <node> list start_list attribute
%type <node> boolean_expression boolean_factor boolean_term expression term factor
%type <node> else_clause

%start program

%%

program:
    statement_list
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
      type IDENTIFIER { Node *node = create_node("variable", $1); add_child(node, create_node("identifier", $2)); add_child(current_scope, node); }
    | type IDENTIFIER ASSIGN boolean_expression { Node *node = create_node("variable", $1); add_child(node, create_node("identifier", $2)); add_child(node, $4); add_child(current_scope, node); }
    
    | IDENTIFIER ASSIGN boolean_expression { Node *node = create_node("assignment"); add_child(node, create_node("identifier", $1)); add_child(node, $3); add_child(current_scope, node); }
    | attribute ASSIGN boolean_expression { Node *node = create_node("attribute_assignment"); add_child(node, $1); add_child(node, $3); add_child(current_scope, node); } 
    
    | IF boolean_expression THEN block { Node *node = create_node("if"); add_child(node, $2); add_child(node, $4); add_child(current_scope, node); }
    | IF boolean_expression THEN block else_clause { Node *node = create_node("if"); add_child(node, $2); add_child(node, $4); add_child(node, $5); add_child(current_scope, node); }
    | WHILE boolean_expression REPEAT block { Node *node = create_node("while"); add_child(node, $2); add_child(node, $4); add_child(current_scope, node); }
    
    | FORM IDENTIFIER form_block { Node *node = create_node("form"); add_child(node, create_node("identifier", $2)); add_child(node, $3); add_child(current_scope, node); }
    | ON OPEN_SQR IDENTIFIER CLOSE_SQR DISPLAY OPEN_PAR boolean_expression CLOSE_PAR { Node *node = create_node("display"); add_child(node, create_node("identifier", $3)); add_child(node, $7); add_child(current_scope, node); }
    | CANCEL { Node *node = create_node("cancel"); add_child(current_scope, node); }
    ;

else_clause:
      ELSE IF boolean_expression THEN block { $$ = create_node("if"); add_child($$, $3); add_child($$, $5); }
    | ELSE IF boolean_expression THEN block else_clause { $$ = create_node("if"); add_child($$, $3); add_child($$, $5); add_child($$, $6); }
    | ELSE block { $$ = $2;}
    ;

type:
      NUMBER_TYPE  { $$ = strdup("number"); }
    | STRING_TYPE  { $$ = strdup("string"); }
    | BOOLEAN_TYPE { $$ = strdup("boolean"); }
    | TIME_TYPE    { $$ = strdup("time"); }
    | DATE_TYPE    { $$ = strdup("date"); }
    ;

start_object:
    OPEN_BRK NEWLINE { $$ = create_scope_node("object"); }
    ;

form_block:
    start_object form_statement_list CLOSE_BRK { exit_scope(); $$ = $1; }
    ;

form_statement_list:
    /* vazio */
    | NEWLINE form_statement_list
    | form_statement NEWLINE form_statement_list
    ;

form_statement:
      FIELD IDENTIFIER field_type field_block { Node *node = create_node("field", $3); add_child(node, create_node("identifier", $2)); add_child(node, $4); add_child(current_scope, node); }
    | ONSUBMIT block { Node *node = create_node("form_onSubmit"); add_child(node, $2); add_child(current_scope, node); }

field_block:
    start_object field_statement_list CLOSE_BRK { exit_scope(); $$ = $1; }
    ;

field_statement_list:
    /* vazio */
    | NEWLINE field_statement_list
    | field_statement NEWLINE field_statement_list
    ;

field_statement:
      REQUIRED { add_child(current_scope, create_node("required")); }
    | TITLE ASSIGN boolean_expression { Node *node = create_node("title"); add_child(node, $3); add_child(current_scope, node); }
    | DESCRIPTION ASSIGN boolean_expression { Node *node = create_node("description"); add_child(node, $3); add_child(current_scope, node); }
    | PLACEHOLDER ASSIGN boolean_expression { Node *node = create_node("placeholder"); add_child(node, $3); add_child(current_scope, node); }
    | DEFAULT ASSIGN boolean_expression { Node *node = create_node("default"); add_child(node, $3); add_child(current_scope, node); }
    | OPTIONS ASSIGN list { Node *node = create_node("options"); add_child(node, $3); add_child(current_scope, node); }
    | ONCHANGE block { Node *node = create_node("field_onChange"); add_child(node, $2); add_child(current_scope, node); }
    ;

field_type:
      NUMBER_TYPE { $$ = strdup("number"); }
    | STRING_TYPE { $$ = strdup("string"); }
    | TIME_TYPE   { $$ = strdup("time"); }
    | DATE_TYPE   { $$ = strdup("date"); }
    | SELECT      { $$ = strdup("select"); }
    ;

field_attribute:
      VALUE       { $$ = strdup("value"); }
    | REQUIRED    { $$ = strdup("required"); }
    | TITLE       { $$ = strdup("title"); }
    | DESCRIPTION { $$ = strdup("description"); }
    | PLACEHOLDER { $$ = strdup("placeholder"); }
    | DEFAULT     { $$ = strdup("default"); }
    | OPTIONS     { $$ = strdup("options"); }
    ;

attribute:
      IDENTIFIER attribute { $$ = $2; add_child($$, create_node("identifier", $1)); }
    | DOT IDENTIFIER attribute { $$ = $3; add_child($$, create_node("identifier", $2)); }
    | DOT field_attribute { $$ = create_node("attribute", $2); }
    // | DOT IDENTIFIER { $$ = create_node("attribute", $2); }

start_list:
    OPEN_SQR NEWLINE { $$ = create_scope_node("list"); }
    ;

list: 
    start_list list_items CLOSE_SQR { exit_scope(); $$ = $1; }
    ;

list_items:
    /* vazio */
    | NEWLINE list_items 
    | boolean_expression COMMA list_items { add_child(current_scope, $1); }
    | boolean_expression NEWLINE { add_child(current_scope, $1); }
    ;

boolean_expression:
      boolean_term { $$ = $1; }
    | boolean_term OR boolean_expression { $$ = create_node("bin_op", "or"); add_child($$, $1); add_child($$, $3); }
    ;

boolean_term:
      boolean_factor { $$ = $1; }
    | boolean_factor AND boolean_term { $$ = create_node("bin_op", "and"); add_child($$, $1); add_child($$, $3); }
    ;

boolean_factor:
      expression { $$ = $1; }
    | expression EQUAL boolean_factor { $$ = create_node("bin_op", "equal"); add_child($$, $1); add_child($$, $3); }
    | expression NOT_EQUAL boolean_factor { $$ = create_node("bin_op", "not_equal"); add_child($$, $1); add_child($$, $3); }
    | expression GREATER boolean_factor { $$ = create_node("bin_op", "greater"); add_child($$, $1); add_child($$, $3); }
    | expression LESS boolean_factor { $$ = create_node("bin_op", "less"); add_child($$, $1); add_child($$, $3); }
    ;

expression:
      term { $$ = $1; }
    | term PLUS expression  { $$ = create_node("bin_op", "plus"); add_child($$, $1); add_child($$, $3); }
    | term MINUS expression { $$ = create_node("bin_op", "minus"); add_child($$, $1); add_child($$, $3); }
    ;

term:
      factor { $$ = $1; }
    | factor MULT term { $$ = create_node("bin_op", "mult"); add_child($$, $1); add_child($$, $3); }
    | factor DIV term { $$ = create_node("bin_op", "div"); add_child($$, $1); add_child($$, $3); }
    ;

factor:
      NUMBER { $$ = create_node("number", &($1)); }
    | STRING { $$ = create_node("string", $1); }
    | BOOLEAN { $$ = create_node("boolean", $1 ? "true" : "false"); }
    | DATE { $$ = create_node("date", $1); }
    | TIME { $$ = create_node("time", $1); }
    | IDENTIFIER { $$ = create_node("identifier", $1); }
    | attribute { $$ = create_node("attribute_access"); add_child($$, $1); }
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
        fprintf(stderr, "use: %s <input_file.form>\n", argv[0]);
        return 1;
    }

    char source_filename[256];
    strcpy(source_filename, argv[1]);
    FILE *source_file = fopen(source_filename, "r");
    if (!source_file) {
        fprintf(stderr, "Error opening the source file: %s\n", source_filename);
        return 1;
    }

    char output_filename[256];
    strcpy(output_filename, source_filename);
    char *dot = strrchr(output_filename, '.');
    (dot) ? strcpy(dot, ".json") : strcat(output_filename, ".json");
    FILE *output_file = fopen(output_filename, "w");
    if (!output_file) {
        fprintf(stderr, "Error opening/creating the output file for the AST");
        return 1;
    }

    yyin = source_file;

    if (yyparse() == 0) {
        printf("Parsing completed successfully.\n");
        save_ast_json(root, output_file); 
        printf("AST saved to JSON file: %s\n", output_filename);
        free_ast(root); 
    }

    fclose(source_file);
    fclose(output_file);
    return 0;
}