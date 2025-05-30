#!/bin/bash

# Verifica se o usuário forneceu um nome de arquivo
if [ $# -ne 1 ]; then
    echo "Uso: $0 <arquivo_entrada>"
    exit 1
fi

# Nome do arquivo passado como argumento
INPUT_FILE=$1

# Compila o código Flex
flex lexer.l
if [ $? -ne 0 ]; then
    echo "Erro na compilação do Flex"
    exit 1
fi

# Compila o código Bison
bison -d parser.y
if [ $? -ne 0 ]; then
    echo "Erro na compilação do Bison"
    exit 1
fi

# Compila tudo junto
g++ parser.tab.c lex.yy.c -o parser
if [ $? -ne 0 ]; then
    echo "Erro na compilação final"
    exit 1
fi

# Executa o parser com o arquivo de entrada
./parser "$INPUT_FILE"