import sys
from antlr4.error.ErrorListener import ErrorListener

class GenshinLangErrorListener(ErrorListener):
    def __init__(self):
        super(GenshinLangErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"Błąd składni w linii {line}, kolumna {column}, symbol {msg}")
        sys.exit(1)
