#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
import math

class flat_stmt(Stmt):
    #flat_stmt is a subclass of Stmt
    def __init__(self, nodes):
        Stmt.__init__(self, nodes)

class python_compiler:
    
    flat_stmt.nodes = []
    
    @staticmethod
    def treeFlatten(ast):
        python_compiler.treeFlatten_helper(ast, 0)
        ast2 = Module(None, Stmt(flat_stmt.nodes))
        print('\nPython AST\n----------')
        print(ast)
        print('\n\nFlattened AST\n-------------')
        print(ast2)
        print('\n')
        return ast2


    @staticmethod
    def treeFlatten_helper(ast, tmp_num):
        
        if isinstance(ast, Module):
            python_compiler.treeFlatten_helper(ast.node, tmp_num)
            return 0

        elif isinstance(ast,  Stmt):
            for node in ast.nodes:
                length = len(flat_stmt.nodes)
                tmp_num = length
                python_compiler.treeFlatten_helper(node, tmp_num)
                #tmp_num += 1
            return tmp_num
            
        elif isinstance(ast, Printnl):
            print_var = python_compiler.treeFlatten_helper(ast.nodes[0], tmp_num)
            new_stmt = 'print tmp' + str(print_var)
            flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
            return print_var

        elif isinstance(ast, Discard):
            python_compiler.treeFlatten_helper(ast.expr, tmp_num)
            return tmp_num

        elif isinstance(ast, Assign):
            varName = "__"+ast.nodes[0].name
            # right_val is the value that we are assigning our name to
            right_val = python_compiler.treeFlatten_helper(ast.expr, tmp_num)
            new_stmt = varName + ' = tmp' + str(right_val)
            flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
            return right_val

        elif isinstance(ast, Add):
            # recurse down BOTH sides of tree
            left_val = python_compiler.treeFlatten_helper(ast.left, tmp_num)
            right_val = python_compiler.treeFlatten_helper(ast.right, left_val + 1)
            new_stmt = 'tmp' + str(right_val + 1) + ' = tmp' + str(left_val) + ' + tmp' + str(right_val)
            flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
            return right_val + 1

        elif isinstance(ast, UnarySub):
            neg_var = python_compiler.treeFlatten_helper(ast.expr, tmp_num)
            new_stmt = 'tmp' + str(neg_var + 1) + ' = -tmp' + str(neg_var)
            flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
            return neg_var + 1
            
        # CallFunc, Name, and Const are base cases
        elif isinstance(ast, CallFunc):
            # for now we just append input(), will have to expand for
            # future subsets of Python
            new_stmt = 'tmp' + str(tmp_num) + ' = input()'
            flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
            return tmp_num
                
        elif isinstance(ast, Name):
            ast.name = "__"+ast.name
            new_stmt = 'tmp' + str(tmp_num) + ' = ' + ast.name
            flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
            return tmp_num

        elif isinstance(ast, Const):
            new_stmt = 'tmp' + str(tmp_num) + ' = ' + str(ast.value)
            flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
            return tmp_num
            
        else:
            raise Exception("Error: Unrecognized node type")
