#!/bin/bash

# Verifica se o usuário forneceu um nome de arquivo
if [ $# -ne 1 ]; then
    echo "Uso: $0 <arquivo_entrada>"
    echo "Erro: Nenhum arquivo de entrada fornecido."
else
    INPUT_FILE=$1

    # Compila o código Flex
    if ! flex lexer.l; then
        echo "Erro na compilação do Flex"
        return
    fi

    # Compila o código Bison
    if ! bison -d parser.y; then
        echo "Erro na compilação do Bison"
        return
    fi

    # Compila tudo junto
    if ! g++ parser.tab.c lex.yy.c -o parser; then
        echo "Erro na compilação final"
        return
    fi

    # Executa o parser com o arquivo de entrada
    if ! ./parser "$INPUT_FILE"; then
        echo "Erro ao executar o parser"
        return
    fi
fi