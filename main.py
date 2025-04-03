import sys
import antlr4
from generated.GenshinLangLexer import GenshinLangLexer
from generated.GenshinLangParser import GenshinLangParser
from GenshinLangActions import GenshinASTBuilder as GenshinLangBaseListener
from LLVMGenerator import LLVMGenerator as IRGenerator

class GenshinLangListener(GenshinLangBaseListener):
    def enterProgram(self, ctx):
        return super().enterProgram(ctx)

# def main ():
#     input_stream = antlr4.FileStream(sys.argv[1])
#     lexer = GenshinLangLexer(input_stream)
#     token_stream = antlr4.CommonTokenStream(lexer)
#     parser = GenshinLangParser(token_stream)

#     parse_tree = parser.program()
#     listener = GenshinLangListener()

#     walker = antlr4.ParseTreeWalker()
#     walker.walk(listener, parse_tree)

# if __name__ == '__main__':
#     main()

def main():
    input_stream = antlr4.FileStream(sys.argv[1])
    lexer = GenshinLangLexer(input_stream)
    tokens = antlr4.CommonTokenStream(lexer)
    parser = GenshinLangParser(tokens)
    tree = parser.program()

    ast_builder = GenshinLangBaseListener()
    walker = antlr4.ParseTreeWalker()
    walker.walk(ast_builder, tree)

    ir_generator = IRGenerator()
    llvm_ir = ir_generator.generate(ast_builder.ast)

    with open("output.ll", "w") as f:
        f.write(llvm_ir)

    print("LLVM IR successfully written to output.ll")

if __name__ == "__main__":
    main()