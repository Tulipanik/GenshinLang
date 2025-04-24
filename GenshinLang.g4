grammar GenshinLang;

// Parser
program: statement* EOF;

statement:
	variable
	| variableAssign
	| array
	| matrix
	| arrayElemAssign
	| matrixAssign
	| printStat
	| readStat
	| expressionStat
	| ifStat;

variable: TYPE IDENTIFIER;
variableAssign: TYPE? IDENTIFIER ASSIGN elemToAssign;

arrayElemAssign:
	IDENTIFIER '[' expression ']' ASSIGN elemToAssign;

matrixAssign:
	IDENTIFIER '[' expression ']' '[' expression ']' ASSIGN elemToAssign;

array: '[' expression (',' expression)* ']';
matrix: '[' row (',' row)* ']';
row: '[' expression (',' expression)* ']';

printStat: 'print' '(' printElement (',' printElement)* ')';

printElement: expression | STRING | IDENTIFIER;

readStat: READ '(' IDENTIFIER ')';

elemToAssign: expression | array | matrix;

expressionStat: expression;

expression: term ((PLUS | MINUS) term)*;

term: factor ((MUL | DIV) factor)*;

ifStat: 'if' '(' boolExpr ')' '{' statement* '}' ('else' '{' statement* '}')?;
    
boolExpr: boolExpr ('&&' | '||') boolExpr
    | '!' boolExpr
    | expression COMPARSION expression
    | BOOLEAN
    | IDENTIFIER;

factor:
	MINUS NUMBER
	| NUMBER
	| IDENTIFIER
	| IDENTIFIER '[' expression ']'
	| IDENTIFIER '[' expression ']' '[' expression ']';

// Lexer
TYPE: 'int' | 'float' | 'double' | 'boolean';
PRINT: 'print';
READ: 'read';
BOOLEAN: 'true' | 'false';
COMPARSION: '==' | '!=' | '<' | '>' | '<=' | '>=';
// AND: '&&';
// OR: '||';
// XOR: '^';
NEG: '!';
PLUS: '+';
MINUS: '-';
MUL: '*';
DIV: '/';
ASSIGN: '=';
STRING: '"' ( '\\"' | ~'"')* '"';

NUMBER: [0-9]+ ('.' [0-9]+)?;
IDENTIFIER: [a-zA-Z0-9_]+;
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' .*? '\r'? '\n' -> skip;