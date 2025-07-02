from lexer import *
from parser import *
from semantic_analyzer import *
from tac_generator import *
from tac_optimizer import optimize
from vm_code_generator import *
from VM import *
import sys
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Leitor de parâmetros para execução de arquivos .exp")

    # Argumento obrigatório: arquivo .exp
    parser.add_argument("-a", "--arquivo", type=str, help="Arquivo de entrada com extensão .exp")

    # Flags booleanas
    parser.add_argument("-p", "--processar", action="store_true", help="Executar o código do arquivo")
    parser.add_argument("-o", "--otimizar", action="store_true", help="Aplicar otimizações")
    parser.add_argument("-v", "--verbose", action="store_true", help="Printar saídas")

    args = parser.parse_args()

    # Validação da extensão
    if not args.arquivo.endswith(".exp"):
        print("Erro: o arquivo deve ter extensão '.exp'")
        sys.exit(1)

    if not os.path.isfile(args.arquivo):
        print(f"Erro: arquivo '{args.arquivo}' não encontrado.")
        sys.exit(1)

    return args

def execute(source_code, run, opt, verbose):
    if verbose:
        print("Conteúdo do arquivo lido com sucesso:")
        print(source_code)

    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    stream = TokenStream(tokens)

    if verbose:
        print("Tokens:")
        for t in stream.tokens:
            print(t)

    parser = Parser(stream)
    parsed_ast = parser.parse_program()

    if verbose:
        print("\nAST gerada:")
        for node in parsed_ast.statements:
            print(node)

    analyzer = SemanticAnalyzer()
    analyzer.visit(parsed_ast)

    if verbose:
        print("\nTabela de Símbolos Global:")
        print(analyzer.global_scope)

    tacgen = TACGenerator(analyzer.global_scope)
    instructions = tacgen.visit(parsed_ast)

    if verbose:
        print("\nInstruções:")
        for instr in instructions:
            print(instr)

    if opt:
        optimized = optimize(instructions)

        if verbose:
            print("\Optimizado:")
            for instr in optimized:
                print(instr)
    else:    
        optimized = instructions 

    vmgen = VMCodeGenerator(optimized, analyzer.global_scope)
    vm_code = vmgen.generate()

    if verbose:
        print("\VM Code:")
        for line in vm_code:
            print(line, end=",\n")

    if run:
        vm = VirtualMachine()
        vm.run(vm_code)


if __name__ == "__main__":

    args = parse_args()

    print(f"Arquivo: {args.arquivo}")
    print(f"Executar: {args.processar}")
    print(f"Otimizar: {args.otimizar}")
    print(f"Verbose: {args.verbose}")

    try:
        with open(args.arquivo, "r", encoding="utf-8") as f:
            source_code = f.read()

            execute(source_code, args.processar, args.otimizar, args.verbose)

    except FileNotFoundError:
        print(f"Arquivo não encontrado: {args.arquivo}")
        sys.exit(1)

