%{
    #include <stdio.h>
    #include "parser.tab.h"

    char *str_parse(const char *str) {
        size_t len = strlen(str);
        char *str_parsed = (char *)malloc(len); 
        strncpy(str_parsed, str + 1, len - 2); 
        str_parsed[len - 2] = '\0'; 
        return str_parsed;
    }

%}

DIGIT   [0-9]
LETTER  [a-zA-Z]

NUMBER_VAL {DIGIT}+(\.{DIGIT}+)?

STRING_VAL ["]([^\n\"])*["]

IDENTIFIER  {LETTER}({LETTER}|{DIGIT}|"_")*

%%

"false"     { yylval.boolean = 0; return BOOLEAN; }
"true"      { yylval.boolean = 1; return BOOLEAN; }

"+"         { return PLUS; }
"-"         { return MINUS; }
"*"         { return MULT; }
"/"         { return DIV; }
"="         { return ASSIGN; }
"("         { return OPEN_PAR; }
")"         { return CLOSE_PAR; }
"{"         { return OPEN_BRK; }
"}"         { return CLOSE_BRK; }
"["         { return OPEN_SQR; }
"]"         { return CLOSE_SQR; }

"."         { return DOT; }
","         { return COMMA; }
";"         { return SEMICOLON; }

"not"       { return NOT; }
"and"       { return AND; }
"or"        { return OR; }

"=="        { return EQUAL; }
"!="        { return NOT_EQUAL; }
">"         { return GREATER; }
"<"         { return LESS; }

"if"        { return IF; }
"then"      { return THEN; }
"else"      { return ELSE; }
"while"     { return WHILE; }
"repeat"    { return REPEAT; }
"new"       { return NEW; }

"Number"    { return NUMBER_TYPE; }
"String"    { return STRING_TYPE; }
"Boolean"   { return BOOLEAN_TYPE; }
"Time"      { return TIME_TYPE; }
"Date"      { return DATE_TYPE; }

"Field"     { return FIELD; }
"Form"      { return FORM; }
"on"        { return ON; }
"display"   { return DISPLAY; }
"cancel"    { return CANCEL; }

"Select"    { return SELECT; }
"value"     { return VALUE; }
"title"     { return TITLE; }
"description" { return DESCRIPTION; }
"placeholder" { return PLACEHOLDER; }
"default"   { return DEFAULT; }
"options"   { return OPTIONS; }
"required"  { return REQUIRED; }
"onChange"  { return ONCHANGE; }
"onSubmit"  { return ONSUBMIT; }

{NUMBER_VAL}  { yylval.number = atof(yytext);   return NUMBER; }

["](2[0:4]|[0-1][0-9])[:][0-5][0-9]["] { yylval.string = str_parse(yytext); return TIME; }
["][0-9][0-9][0-9][0-9][-](1[0-2]|0[0-9])[-]([0-2][0-9]|3[0-1])["] { yylval.string = str_parse(yytext); return DATE; }

{STRING_VAL} { yylval.string = str_parse(yytext); return STRING; }


{IDENTIFIER} { yylval.string = strdup(yytext); return IDENTIFIER; }

\/\/[^\n]*  { /* Ignorar comentários  */ }
[ \t\r]+    { /* Ignorar espaços */ }
"\n"        { return NEWLINE; }

.           { printf("invalid: %s\n", yytext); }
%%

int yywrap() {
    return 1;
}
