#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
from python_compiler import *

ast = compiler.parse("x = (4 + 1) + - 2; print 3 + ( 5 + 2 + x) +  - (1 + input() )")
python_compiler.treeFlatten(ast)
