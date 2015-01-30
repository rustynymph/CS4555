tokens = ('PRINT','INT','PLUS')
t_PRINT = r'print'
t_PLUS = r'\+'
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

def p_plus_epression(t):
	'expression : epression PLUS epression'
	t[0] = Add((t[1],t[3]))

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