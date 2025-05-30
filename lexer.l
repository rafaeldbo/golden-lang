%{
    #include <stdio.h>
    #include "parser.tab.h"
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
"submit"    { return SUBMIT; }

"Select"    { return SELECT; }
"title"     { return TITLE; }
"description" { return DESCRIPTION; }
"placeholder" { return PLACEHOLDER; }
"options"   { return OPTIONS; }
"required"  { return REQUIRED; }
"validator" { return VALIDATOR; }

{NUMBER_VAL}  { yylval.number = atof(yytext);   return NUMBER; }

["][0-9][0-9][:][0-9][0-9]["] { yylval.string = strdup(yytext); return TIME; }
["][0-9][0-9][0-9][0-9][-](1[0-2]|0[0-9])[-]([0-2][0-9]|3[0-1])["] { yylval.string = strdup(yytext); return DATE; }

{STRING_VAL} { yylval.string = strdup(yytext); return STRING; }


{IDENTIFIER} { yylval.string = strdup(yytext); return IDENTIFIER; }

\/\/[^\n]*  { /* Ignorar comentários  */ }
[ \t\r]+    { /* Ignorar espaços */ }
"\n"        { return NEWLINE; }

.           { printf("invalid: %s\n", yytext); }
%%

int yywrap() {
    return 1;
}
