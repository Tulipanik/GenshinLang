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
	| expressionStat;

variable: TYPE IDENTIFIER;
variableAssign: TYPE? IDENTIFIER ASSIGN elemToAssign;

arrayElemAssign:
	IDENTIFIER '[' expression ']' ASSIGN elemToAssign;

matrixAssign:
	IDENTIFIER '[' expression ']' '[' expression ']' ASSIGN elemToAssign;

array: '[' expression (',' expression)* ']';
matrix: '[' row (',' row)* ']';
row: '[' expression (',' expression)* ']';

printLiteral: (STRING | IDENTIFIER | expression)*;

printStat: PRINT '(' printLiteral ')';
readStat: READ '(' IDENTIFIER ')';

elemToAssign: expression | array | matrix;

expressionStat: expression;

expression: term ((PLUS | MINUS) term)*;

term: factor ((MUL | DIV) factor)*;

factor:
	NUMBER
	| STRING
	| IDENTIFIER
	| IDENTIFIER '[' expression ']'
	| IDENTIFIER '[' expression ']' '[' expression ']';

// Lexer
TYPE: 'int' | 'float' | 'double' | 'boolean';
PRINT: 'print';
READ: 'read';
AND: '&&';
OR: '||';
XOR: '^';
NEG: '!';
TRUE: 'true';
FALSE: 'false';
PLUS: '+';
MINUS: '-';
MUL: '*';
DIV: '/';
ASSIGN: '=';
STRING: '"' ( '\\"' | ~'"')* '"';

NUMBER: [0-9]+ ('.' [0-9]+)?;
IDENTIFIER: [a-zA-Z0-9_]+;
WS: [ \t\r\n]+ -> skip;