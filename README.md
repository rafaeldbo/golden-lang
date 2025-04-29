# Golden-Lang

Repositório para o projeto final da disciplina `Lógica da Computação` Insper 2025.1.

O projeto consiste em uma Linguagem de programação voltada para a construção de formulários. O objetivo é facilitar a criação de formulários complexos que possui diferentes campos, validação de entradas e estruturas complexas. 

A linguagem será estruturada com uma sintaxe simples, mas completa o suficiente para permitir a criação de formulários complexos. A linguagem compiará diretamente para HTML+JS, permitindo que os formulários sejam utilizados em qualquer navegador moderno.

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
TIME    = HOUR, ":", MINUTE ;

YEAR    = DIGIT, DIGIT, DIGIT, DIGIT ;
MONTH   = ( 0, ( 1 | ... | 9 ) ) | ( 1, ( 0 | 1 | 2 ) ) ;
DAY     = ( ( 0 | 1 | 2 ), DIGIT ) | ( 3, ( 0 | 1 ) ) ;
DATE    = YEAR, "-", MONTH, "-", DAY ;

(* Expressões *)
BOOLEAN_EXPRESSION = BOOLEAN_TERM, "or", BOOLEAN_TERM ;
BOOLEAN_TERM       = BOOLEAN_FACTOR, "and", BOOLEAN_FACTOR ;
BOOLEAN_FACTOR     = EXPRESSION, ( "==" | "!="  | ">" | "<" | ">=" | "<="), EXPRESSION ;

EXPRESSION = TERM, { ("+" | "-"), TERM } ;
TERM       = FACTOR, { ("*" | "/"), FACTOR } ;
FACTOR     = (("+" | "-" | "not" ), FACTOR) | NUMBER | BOOL | STRING | "(", EXPRESSION, ")" | IDENTIFIER ;

(* Estuturas de Variáveis *)
TYPE       = ( "Text" | "Number" | "Date" | "Hour" | "bool" ) ;
IDENTIFIER = LETTER, { LETTER | DIGIT | "_" } ;
VARIABLE   = "var", IDENTIFIER, ":", TYPE, [ "=", EXPRESSION ], "\n" ;
ASSIGNMENT = IDENTIFIER, "=", EXPRESSION ;

(* Estruturas de Código *)
CODE_STATEMENT = ( λ | ASSIGNMENT | IF | LOOP | ), "\n" ;
CODE_BLOCK     = "{", "\n", { CODE_STATEMENT }, "}" ;

IF   = "when", BOOLEAN_EXPRESSION, "then", "{", { CODE_STATEMENT }, "}", [ "else", "{", { CODE_STATEMENT }, "}" ] ;
LOOP = "while", BOOLEAN_EXPRESSION, "repeat", "{", { CODE_STATEMENT }, "}" ;

(* Funções Básicas *)	
DISPLAY = "on", "[", IDENTIFIER, "]", "display", "(" STRING, ")" ;
FORM_RENDER = "render", "(", IDENTIFIER, ")" ;

(* Estruturas de Formulário *)
FIELD_TYPE = ( TYPE | "Select" | "Checkbox" ) ;
FIELD      = "Field", IDENTIFIER, ":", FIELD_TYPE, "{", { FIELD_STATEMENT }, "}" ;
FIELD_STATEMENT = ( 
    "required" | 
    ( "placeholder", "=", STRING ) | 
    ( "title", "=", "STRING" ) |
    ( "description", "=", STRING ) | 
    ( "default", "=", ( NUMBER | STRING | BOOLEAN | DATE | TIME ) ) | 
    ( "options", "=", "[", { STRING }, "]" ) |
    ( "on_change_validator", CODE_BLOCK ) |
    ( "on_submit_validator", CODE_BLOCK ) 
), ";" ;
FORM = "Form", IDENTIFIER , "{" { FIELD }, "}", "\n" ;

(* Bloco Inicial *)
MASTER_BLOCK = { ( CODE_STATEMENT | FORM ) } ;
```

## Exemplo de Código
```golden-lang
Form apresentacao {
    Field nome: Text {
        required;
        placeholder = "Digite seu nome";
        title = "Nome";
        description = "Digite seu nome completo";
    }
    Field idade: Number {
        required;
        placeholder = "Digite sua idade";
        title = "Idade";
        description = "Digite sua idade em anos";
    }
    Field genero: Select {
        required;
        placeholder = "Selecione seu gênero";
        title = "Gênero";
        description = "Selecione seu gênero";
        options = ["Masculino", "Feminino", "Outro"];
    }
    Field data_nascimento: Date {
        required;
        placeholder = "Digite sua data de nascimento";
        title = "Data de Nascimento";
        description = "Qual é sua data de nascimento? Responda no formato YYYY-MM-DD";
    }
    Field hora_almoco: Hour {
        required;
        placeholder = "Digite a sua hora de almoço";
        title = "Hora do almoço";
        description = "A que horas você costuma almoçar? Responda no formato: HH:MM";
    }
    Field curiosidade: Text {
        placeholder = "Digite uma curiosidade sobre você";
        title = "Curiosidade";
        description = "Fale uma coisa interessante sobre você, algo que ninguém sabe!";
    }
}

Form prato_comida {
    Field prato: Text {
        required;
        placeholder = "Digite o nome do prato";
        title = "Prato";
        description = "Qual prato você está com vontate de comer?";
    }
}

var x: Number = 10
vat i: Number = 0
on[PAGE]display("Quem é você? Se apresente!")
render(presentacao)
on[PAGE]display("Quais pratos você gostaria de comer? Nos diga 10!")
while i < 10 repeat {
    i = i + 1
    on[PAGE]display(i + "º prato")
    render(prato_comida)
}>