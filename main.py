import sys
import antlr4
from generated.GenshinLangLexer import GenshinLangLexer
from generated.GenshinLangParser import GenshinLangParser
from GenshinLangErrorListener import GenshinLangErrorListener
from GenshinLangActions import GenshinASTBuilder
from LLVMGenerator import LLVMGenerator

def main():
    if len(sys.argv) < 2:
        print("Użycie: python main.py <ścieżka_do_pliku>")
        sys.exit(1)

    input_stream = antlr4.FileStream(sys.argv[1])

    lexer = GenshinLangLexer(input_stream)
    lexer.removeErrorListeners()
    error_listener = GenshinLangErrorListener()
    lexer.addErrorListener(error_listener)

    tokens = antlr4.CommonTokenStream(lexer)

    parser = GenshinLangParser(tokens)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.program()

    ast_builder = GenshinASTBuilder()
    walker = antlr4.ParseTreeWalker()
    walker.walk(ast_builder, tree)

    ir_generator = LLVMGenerator()
    llvm_ir = ir_generator.generate(ast_builder.ast)

    with open("output.ll", "w") as f:
        f.write(llvm_ir)

    print("Kod LLVM IR został pomyślnie zapisany do pliku output.ll")

if __name__ == "__main__":
    main()
