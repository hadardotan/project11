from enum import Enum
from Compiler.JackGrammar import *

# This module provides services for creating, populating, and using a symbol
# table. Recall that each symbol has a scope from which it is visible
# in the source code. In the symbol table, each symbol is given a running
# number (index) within the scope, where the index starts at 0 and is
# reset when starting a new scope.

# TODO :you will probably need to use two separate hash tables to implement the symbol
# table: one for the class-scope and another one for the subroutine-scope. When a new subroutine
# is started, the subroutine-scope table should be cleared.


# class Kind(Enum):
#     """
#     enum represent kind of identifier may appear in the symbol table
#     """
#
#
#     def get_seg(self):
#         if self is Kind.var:
#             return K_VAR
#         elif self is Kind.field:
#             return K_FIELD
#         elif self is Kind.arg:
#             return K_ARG
#         elif self is Kind.static:
#             return K_STATIC

STATIC = 1
FIELD = 2
ARG = 3
VAR = 4


C_TYPE = 0
C_KIND = 1
C_INDEX = 2

class SymbolTable(object):

    """
    A symbol table that associates names with information needed for Jack
    compilation: type, kind, and running index. The symbol table has 2
    nested scopes (class/subroutine).
    """
    def __init__(self):
        """
        Creates a new empty symbol table contains:
        -class_table
        -subroutine_table

        each field in a table looks like:

        name : (type, kind, running_index=counter)
        """

        self.class_table = {}
        self.subroutine_table = {}
        self.counter = {VAR : 0, STATIC : 0, ARG : 0, FIELD : 0}

    def start_subroutine(self):
        """
        Starts a new subroutine scope (i.e. erases
        all names in the previous subroutine’s scope.)

        empty subroutine table and arg and var counters
        :return:
        """

        self.counter[ARG], self.counter[VAR] = 0, 0
        self.subroutine_table = {}


    def define(self, name, type, kind):
        """
        Defines a new identifier of a given name, type, and kind and assigns
        it a running index. STATIC and FIELD identifiers have a class scope,
        while ARG and VAR identifiers have a subroutine scope.

        :param name: string
        :param type: string
        :param kind:(STATIC,FIELD, ARG, or VAR)
        :return:
        """
        if kind == STATIC or kind == FIELD:
            self.class_table[name] = (type, kind, self.counter[kind])
        else:
            self.subroutine_table[name] = (type, kind, self.counter[kind])

        self.counter[kind] += 1


    def varCount(self, kind):
        """
        Returns the number of variables of the given kind already defined in
        the current scope.
        :param kind:STATIC,FIELD, ARG, or VAR
        :return: int
        """
        return self.counter[kind]


    def kindOf(self, name):
        """
        Returns the kind of the named identifier in the current scope.
        Returns NONE if the identifier is unknown in the current scope
        :param name:string
        :return:kind:STATIC,FIELD, ARG, or VAR
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][C_KIND]
        elif name in self.class_table:
            return self.class_table[name][C_KIND]
        # else:
        #     return NO_KIND


    def typeOf(self, name):
        """
        Returns the type of the named identifier in the current scope.
        :param name:string
        :return:string
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][C_TYPE]
        elif name in self.class_table:
            return self.class_table[name][C_TYPE]
        # else:
        #     return NO_TYPE


    def indexOf(self, name):
        """
        Returns the index assigned to named identifier.
        :param name:string
        :return:int
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][C_INDEX]
        elif name in self.class_table:
            return self.class_table[name][C_INDEX]
        # else:
        #     return NO_INDEX

    def check(self):
        for key, value in self.counter.items():
            print(key, value)
