import os, os.path, re, sys
import Compiler.JackTokenizer as tokenizer
import Compiler.JackGrammar as grammar
import Compiler.SymbolTable as symbol
import Compiler.VMWriter as vmwriter

# This class does the compilation itself. It reads its input from a JackTokenizer
# and writes its output into a VMWriter. It is organized as a series of
# compilexxx() methods, where xxx is a syntactic element of the Jack language.
# The contract between these methods is that each compilexxx() method should
# read the syntactic construct xxx from the input, advance() the tokenizer
# exactly beyond xxx, and emit to the output VM code effecting the semantics
# of xxx.Thus compilexxx() may only be called if indeed xxx is the next
# syntactic element of the input.If xxx is a part of an expression and thus
# has a value, then the emitted code should compute this value and leave it
# at the top of the VM stack.

#TODO : understand how different from last compiler


NEW_LINE = "\n"


class CompilationEngine(object):
    def __init__(self, input_file, output_file):
        """
        Creates a new compilation engine with the
        given input and output. The next routine
        called must be compileClass().
        :param input_file:
        """
        self.tokenizer = tokenizer.JackTokenizer(input_file, output_file)
        self.symbol_table = symbol.SymbolTable()
        self.vm = vmwriter.VMwriter()
        self.input = input_file  # already open :)
        self.output = output_file  # already open :)
        self.class_name = "" # current class name
        self.current_subroutine_type = 0
        self.current_subroutine_name = ""
        self.type_list = [grammar.K_INT, grammar.K_CHAR, grammar.K_BOOLEAN]
        self.label_counter = 0
        self.tokenizer.advance()

        self.compile_class()


    def compile_class(self):
        """
        HADAR

        Compiles a complete class.
        :return:
        """
        if self.tokenizer.current_value != grammar.K_CLASS:
            raise ValueError("No class found in the file")


        #class name
        self.tokenizer.advance()
        # add class type to list of types
        self.type_list.append(self.tokenizer.current_value)
        self.compile_identifier()

        # {
        self.tokenizer.advance()
        self.checkSymbol("{")

        # classVarDec*
        self.tokenizer.advance()
        if self.tokenizer.current_value in [grammar.K_STATIC, grammar.K_FIELD]:
            while(self.compile_class_var_dec(False)):
                self.tokenizer.advance()

        # subroutineDec*

        if self.tokenizer.current_value in [grammar.K_CONSTRUCTOR,
                                            grammar.K_FUNCTION, grammar.K_METHOD]:
            while(self.compile_subroutine(False)):
                self.tokenizer.advance()

        # }
        self.checkSymbol("}")



    def compile_class_var_dec(self, raise_error=True):
        """
        HADAR


        Compiles a static declaration or a field
        declaration.
        :return:
        """
        # Check if there is a classVarDec
        # 'static' or 'field'
        if self.tokenizer.current_value in [grammar.K_STATIC, grammar.K_FIELD]:
            kind = grammar.keyword_2_kind[self.tokenizer.current_value]
        else:
            if raise_error:
                raise ValueError("No 'static' or 'field' found")
            else:
                return False

        self.compile_declaration(kind)


    def compile_subroutine_var_dec(self, raise_error=True):
        """
        HADAR

        :param raise_error:
        :return:
        """
        # 'var'
        if self.tokenizer.current_value == grammar.K_VAR:
            kind = grammar.keyword_2_kind[self.tokenizer.current_value]
        else:
            if raise_error:
                raise ValueError("No 'var' found")
            else:
                return False

        self.compile_declaration(kind)



    def compile_declaration(self, kind):
        """
        HADAR

        :param kind:
        :return:
        """

        #type
        self.tokenizer.advance()
        type = self.compile_type()

        # varName
        self.tokenizer.advance()
        name = self.compile_identifier()

        # add to symbol table
        self.symbol_table.define(name, type, kind)


        # (',' varName)*
        more_vars = True
        self.multiple_varNames(more_vars, type, kind)

        # ;
        self.tokenizer.advance()
        self.checkSymbol(";")



    def multiple_varNames(self, more_vars, current_type, kind):
        """
        HADAR

        Compiles all the variables (if there are).
        It is used to represent (',' varName)*

        :param more_vars: more_vars True if there are more varriables, false otherwise
        :param current_type: last var type
        :return:
        """
        #TODO : check if 2 different kinds can be in the same line
        while (more_vars):
            # ','
            if self.tokenizer.get_next()[0] == ",":

                self.tokenizer.advance() # ,

                # type (if applicable)
                if self.tokenizer.get_next()[0] in self.type_list: #new type

                    self.tokenizer.advance()
                    type = self.compile_type(False)
                else:
                    type = current_type

                # varName
                self.tokenizer.advance()
                name = self.compile_identifier()

                # add to symbol table
                self.symbol_table.define(name, type, kind)

            else:
                more_vars = False



    def compile_type(self, raise_error=True):
        """
        HADAR

        checks that current_value in type list
        :return: type
        """
        if self.tokenizer.current_value in self.type_list:
            return self.tokenizer.current_value
        else:
            if raise_error:
                raise ValueError("No type found")
            else:
                return False



    def compile_expression_list(self):
        """
        Compiles a (possibly empty) comma separated list of expressions.

        ALGORITHM 4: A recursive postfix traversal algorithm for evaluating
        an expression tree by generating commands in a stack-based language.
        Code(exp):
        if exp is a number n then output “push n”
        if exp is a variable v then output “push v”
        if exp = (exp1 op exp2) then Code(exp1); Code(exp2) ; output “op”
        if exp = op(exp1) then Code(exp1) ; output “op”
        if exp = f(exp1 … expN) then Code(exp1) … Code(expN); output “call f”

        :return:
        """







    def compile_identifier(self,raise_error=True):
        """
        checks that current_type is identifier
        :return: current_value
        """
        if self.tokenizer.current_token_type == grammar.IDENTIFIER:
            return self.tokenizer.current_value
        else:
            if raise_error:
                raise ValueError("No identifier found")
            else:
                return False




    def compile_subroutine(self, raise_error=True):
        """
        Compiles a complete method, function, or constructor.

        -A Jack subroutine xxx() in a Jack class Yyy is compiled into a VM
        function called Yyy.xxx.
        - A Jack function or constructor with k arguments is compiled into a
         VM function with k arguments.
        -A Jack method with k arguments is compiled into a VM function with k+1 arguments.
        The first argument (argument number 0) always refers to the this object.
        :return:
        """
        if self.is_subroutine():
            self.current_subroutine_type = self.tokenizer.current_value
        else:
            if raise_error:
                raise ValueError("No keyword found in subroutine")
            else:
                return False

        # void or type
        self.tokenizer.advance()
        type = self.tokenizer.current_value
        if self.current_is_void_or_type():
            return_type = self.tokenizer.current_value
        else:
            if raise_error:
                raise ValueError("No keyword found in subroutine")
            return False

        # subroutine name
        self.tokenizer.advance()
        if self.tokenizer.current_token_type == grammar.IDENTIFIER:
            self.current_subroutine_name = self.tokenizer.current_value
        else:
            if raise_error:
                raise ValueError("No keyword found in subroutine")
            return False

        #open symbol table

        self.symbol_table.start_subroutine()
        if self.current_subroutine_type == grammar.K_METHOD:
            self.symbol_table.define('this', self.class_name, grammar.K_ARG)

        # (
        self.tokenizer.advance()
        self.checkSymbol("(")

        # parameterList
        self.tokenizer.advance()
        if self.compile_parameter_list() is not False:
            self.tokenizer.advance()
        else:
            if raise_error:
                raise ValueError("illegal parameter list in subroutine")
            return False

        # )
        self.checkSymbol(")")

        # subroutine body
        self.tokenizer.advance()




    def compile_subroutineBody(self):
        """
        HADAR

        compiles subroutines body
        :return:
        """
        # {
        self.checkSymbol("{")

        # varDecs*
        self.tokenizer.advance()
        more_vars = True
        while (more_vars):
            if self.compile_subroutine_var_dec(False) is False:
                break
            self.tokenizer.advance()

            if self.tokenizer.current_value != "var":
                more_vars = False

        # write function to vm file
        self.write_to_vm_function_dec()

        # statements
        self.compile_statements()

        # }
        self.checkSymbol("}")



    def get_vm_function_name(self):
        """
        HADAR
        A Jack subroutine xxx() in a Jack class Yyy is compiled into a VM
        function called Yyy.xxx.

        :return: vm function name
        """
        return self.class_name+'.'+self.current_subroutine_name



    def write_to_vm_function_dec(self):
        """
        HADAR

        writes "function function_name num_of_vars"
        for example : "function BankAccount.commission 0 "

        loads this pointer according to subroutine type

        :return:
        """
        self.vm.writeFunction(self.get_vm_function_name(),
                              self.symbol_table.varCount(grammar.K_VAR))

        if self.current_subroutine_type == grammar.K_METHOD:
            self.vm.writePush(grammar.K_ARG, 0) # push argument 0
            self.vm.writePop(grammar.POINTER, 0) # pop pointer 0
        elif self.current_subroutine_type == grammar.K_CONSTRUCTOR:
            # push size of object
            self.vm.writePush(grammar.CONST, self.symbol_table.varCount(grammar.field))
            # call Memory.alloc 1
            self.vm.writeCall('Memory.alloc', 1)
            # pop pointer 0
            self.vm.writePop(grammar.POINTER, 0)



    def compile_statements(self):
        """
        HADAR

        Compiles a sequence of statements, not
        including the enclosing {}.
        :return:
        """
        more_statements = True
        # (statement)*
        while (more_statements):
            # TODO :ask ruthi about there lines
            if self.tokenizer.current_value == "/":
                self.tokenizer.advance()
                self.output.write(self.tokenizer.get_next()[0])

            if self.tokenizer.current_value == "if":
                self.compile_if()
                self.tokenizer.advance()

            elif self.tokenizer.current_value == "let":
                self.compile_let()
                self.tokenizer.advance()

            elif self.tokenizer.current_value == "while":
                self.compile_while()
                self.tokenizer.advance()

            elif self.tokenizer.current_value == "do":
                self.compile_do()
                self.tokenizer.advance()

            elif self.tokenizer.current_value == "return":
                self.compile_return()
                self.tokenizer.advance()
            else:
                more_statements = False




    def get_new_label(self):
        """
        HADAR
        :return: 'Ln' n=counter
        """
        self.label_counter += 1
        return 'L'+str(self.label_counter)

    def current_is_void_or_type(self):

        """
        HADAR

        :return: true if void or type, false otherwise
        """
        return (self.tokenizer.current_value == grammar.K_VOID) or self.tokenizer.current_value in self.type_list



    def is_subroutine(self):
        """
        HADAR

        :return: true if current value is subroutine initial
        """

        return self.tokenizer.current_value in [grammar.K_CONSTRUCTOR, grammar.K_FUNCTION, grammar.K_METHOD]

    def compile_parameter_list(self):
        """
        HADAR

        Compiles a (possibly empty) parameter list,
        not including the enclosing ().

        :return:
        """
        more_parameters = True
        while more_parameters:
            if self.is_type():
                type = self.tokenizer.current_value
                self.tokenizer.advance()
                if self.tokenizer.current_token_type == grammar.IDENTIFIER:
                    name = self.tokenizer.current_value
                    #add to symbol table
                    self.symbol_table.define(name, type, grammar.K_ARG)
                    self.tokenizer.advance()

                    if self.tokenizer.current_value == ',':
                        self.tokenizer.advance()
                    elif self.tokenizer.current_value == ')':
                        more_parameters = False

            else:
                return False

        return True


    def compile_var_dec(self, raise_error=True):
        """
        Compiles a var declaration.
        :param raise_error: raises error if True, returns otherwise
        :return:
        """

    def is_type(self):
        """ Checks if the type of the current type is in the type_list
        """

        return (self.tokenizer.current_value in self.type_list)



    def compile_statements(self):
        """
        Compiles a sequence of statements, not
        including the enclosing {}.
        :return:
        """

    def checkSymbol(self, symbol, raise_error=True):
        """ Check if the symbol is in the current value"""
        if self.tokenizer.current_value == symbol:
            return True
        else:
            if raise_error:
                raise ValueError("No symbol " + symbol + " found")



#################################33


    def compile_subroutineCall(self):
        """
        HADAR

        compiles subroutine call and writes vm code


        :return:
        """

        # (subroutineName ( expressionList ))
        if self.tokenizer.get_next()[0] == '(':
            subroutine_name = self.tokenizer.current_value
            self.tokenizer.advance()
            # (
            self.checkSymbol('(')
            self.tokenizer.advance()

            # write to vm : push var1
            self.vm.write_push_var(self.tokenizer.current_value)

            # ,
            if self.tokenizer.get_next()[0] == ',':
                self.tokenizer.advance()
            elif self.tokenizer.get_next()[0] == ')':
                self.tokenizer.advance()

                # write to vm : call subroutine name
                self.vm.write_subroutine_call(subroutine_name)
                return

        # ((className | varName).subroutineName (expressionList))
        else:

            # write vm : push (className | varName)
            self.vm.write_push_var(self.tokenizer.current_value)
            # .
            self.tokenizer.advance()
            self.checkSymbol('.')
            self.tokenizer.advance()
            # subroutine name
            subroutine_name = self.tokenizer.current_value
            self.tokenizer.advance()
            # (
            self.checkSymbol('(')
            self.tokenizer.advance()

            if self.tokenizer.get_next()[0] == ')':
                self.tokenizer.advance()

                # write to vm : call subroutine name
                self.vm.write_subroutine_call(subroutine_name)
                return

        # case there is more than 1 var
        more_vars = True

        while more_vars:
            # write to vm : push var
            self.vm.write_push_var(self.tokenizer.current_value)
            # check if , or )
            self.tokenizer.advance()
            if self.tokenizer.current_value == ')':
                more_vars =False
            elif self.tokenizer.current_value == ',':
                self.tokenizer.advance()
            else:
                raise ValueError("illegal subroutine call")

        # write to vm : call subroutine name
        self.vm.write_subroutine_call(subroutine_name)




























