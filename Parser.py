tokens = ('PRINT','INT','PLUS','MINUS','EQUALS','INPUT')
t_PRINT = r'print'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_EQUALS = r'\='
t_INPUT = r'input()'

def t_INT(t):
	r'\d+'
	try:
		t.value = int(t.value)
	except ValueError:
		print "integer value too large", t.value
		t.value = 0

t_ignore = ' \t'

def t_newline(t):
	r'\n+'
	t.lexer.lineno += t.value.count("\n")

def t_error(t):
	print "Illegal character '%s'" % t.value[0]
	t.lexer.skip(1)

import ply.lex as lex
lex.lex()

from compiler.ast import *

precedence = (
	('nonassoc','PRINT'),
	('left','PLUS')
)

def p_print_statement(t):
	'statement : PRINT expression'
	t[0] = Printnl([t[2]],None)

def p_assign_expression(t):
	'expression : expression EQUALS expression'
	t[0] = Assign([AssName(t[1], 'OP_ASSIGN'), t[3]])

def p_input_expression(t):
	'expression : INPUT'
	t[0] = CallFunc(t[1])

def p_plus_expression(t):
	'expression : expression PLUS expression'
	t[0] = Add((t[1],t[3]))

def p_minus_expression(t):
	'expression : MINUS expression'
	t[0] = UnarySub(t[2])

def p_int_expression(t):
	'expression : INT'
	t[0] = Const(t[1])

def p_error(t):
	print "Syntax error at '%s'" % t.value

import ply.yacc as yacc
yacc.yacc()

import compiler

class Parser:
	@staticmethod
	def parseFile(path):
		return compiler.parseFile(path);

	@staticmethod
	def parse(source):
		return compiler.parse(source);
