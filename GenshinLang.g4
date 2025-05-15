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
	| functionCall
	| expressionStat
	| shortExpression
	| ifStat
	| whileStat
	| forStat
	| functionDeclaration;

functionDeclaration: 'function' IDENTIFIER '(' paramList? ')' block;

functionCall: IDENTIFIER '(' argumentList? ')';

variable: GLOBAL? TYPE IDENTIFIER;
variableAssign: GLOBAL? TYPE? IDENTIFIER ASSIGN elemToAssign;

paramList:TYPE IDENTIFIER (',' TYPE IDENTIFIER)*;

argumentList:
	expression (',' expression)*;

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

shortExpression: IDENTIFIER '++'
	| IDENTIFIER '--'
	| IDENTIFIER SHORTOP elemToAssign
	| IDENTIFIER SHORTOP elemToAssign
	| IDENTIFIER SHORTOP elemToAssign
	| IDENTIFIER SHORTOP elemToAssign;

block: '{' (statement | functionBlock)* '}';
functionBlock: functionDeclaration | returnStatement;

ifStat: 'if' '(' boolExpr ')' block ('else' block)?;

whileStat: 'while' '(' boolExpr ')' block;

forStat: 'for' '(' variableAssign ';' boolExpr ';' (variableAssign | shortExpression) ')' block;
    
boolExpr: boolExpr ('&&' | '||') boolExpr
    | NEG boolExpr
    | expression COMPARSION expression
    | BOOLEAN
    | IDENTIFIER;

factor:
	MINUS NUMBER
	| NUMBER
	| functionCall
	| IDENTIFIER
	| IDENTIFIER '[' expression ']'
	| IDENTIFIER '[' expression ']' '[' expression ']';

returnStatement: 'return' expression?;

// Lexer
TYPE: 'int' | 'float' | 'double' | 'var' | 'boolean';
GLOBAL: 'global';
PRINT: 'print';
READ: 'read';
BOOLEAN: 'true' | 'false';
COMPARSION: '==' | '!=' | '<' | '>' | '<=' | '>=';
SHORTOP: '+=' | '-=' | '*=' | '/=';
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