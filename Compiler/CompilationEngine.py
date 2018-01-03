import os, os.path, re, sys
import Compiler.JackTokenizer as tokenizer
import Compiler.JackGrammar as grammar
import Compiler.SymbolTable as symbol
import Compiler.VMWriter as vmwriter
from collections import deque

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
    def __init__(self, input_file, output_file, dir_classes):
        """
        Creates a new compilation engine with the
        given input and output. The next routine
        called must be compileClass().
        :param input_file:
        """
        self.input = input_file  # already open :)
        self.output = output_file  # already open :)
        self.tokenizer = tokenizer.JackTokenizer(input_file, output_file)
        self.symbol_table = symbol.SymbolTable()
        self.vm = vmwriter.VMwriter(self.output)
        self.class_name = "" # current class name
        self.current_subroutine_type = 0
        self.current_subroutine_name = ""
        self.type_list = grammar.jack_types + grammar.jack_libaries + dir_classes
        self.label_counter = 0
        self.if_counter = 0
        self.while_counter = 0
        self.tokenizer.advance()
        self.symbol_tables = []
        self.compile_class()
        self.return_void = False


    def compile_class(self):
        """
        HADAR
        RUTHI

        Compiles a complete class.
        :return:
        """
        if self.tokenizer.current_value != grammar.K_CLASS:
            raise ValueError("No class found in the file")


        #class name
        self.tokenizer.advance()
        self.class_name = self.tokenizer.current_value
        self.compile_identifier()

        # Create new symbol table
        self.symbol_tables.append(symbol.SymbolTable())

        # {
        self.tokenizer.advance()
        self.checkSymbol("{")

        # classVarDec*
        self.tokenizer.advance()
        if self.tokenizer.current_value in [grammar.K_STATIC, grammar.K_FIELD]:
            more_dec = True
            while(more_dec):
                more_dec = self.compile_class_var_dec(False)
                self.tokenizer.advance()



        # subroutineDec*
        if self.tokenizer.current_value in [grammar.K_CONSTRUCTOR,
                                            grammar.K_FUNCTION, grammar.K_METHOD]:

            while(self.compile_subroutine(False) is not False):
                self.tokenizer.advance()

        # }
        self.checkSymbol("}")

        # delete SymbolTable
        self.symbol_tables.pop()


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

        # check if more vars
        if self.tokenizer.get_next()[0] in [grammar.K_STATIC, grammar.K_FIELD]:
            return True
        else:
            return False



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
        type = self.tokenizer.current_value
        if type not in self.type_list:
            self.type_list += [type]

        # varName
        self.tokenizer.advance()
        name = self.compile_identifier()

        # add to symbol table
        self.symbol_table.define(name, type, kind) # TODO
        self.symbol_tables[self.last_pos()].define(name, type, kind)


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
                if self.tokenizer.get_next()[0] in self.type_list:  # new type
                    self.tokenizer.advance()
                    type = self.tokenizer.current_value
                else:
                    type = current_type

                # varName
                self.tokenizer.advance()
                name = self.compile_identifier()


                # add to symbol table
                self.symbol_table.define(name, type, kind)
                self.symbol_tables[self.last_pos()].define(name, type, kind)

            else:
                more_vars = False



    # def compile_type(self, raise_error=True):
    #     """
    #     HADAR
    #
    #     checks that current_value in type list
    #     :return: type
    #     """
    #     if self.tokenizer.current_value in self.type_list:
    #         return self.tokenizer.current_value
    #     else:
    #         if raise_error:
    #             raise ValueError("No type found")
    #         else:
    #             return False



    def compile_expression_list2(self): # TODO I did it in compile_term. Check if something is missing
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
        self.return_type = self.tokenizer.current_value
        # if self.current_is_void_or_type():
        #     self.return_type = self.tokenizer.current_value
        # else:
        #     if raise_error:
        #         raise ValueError("No keyword found in subroutine")
        #     return False

        # subroutine name
        self.tokenizer.advance()
        if self.tokenizer.current_token_type == grammar.IDENTIFIER:
            self.current_subroutine_name = self.tokenizer.current_value
        else:
            if raise_error:
                raise ValueError("No keyword found in subroutine")
            return False

        #open symbol table

        self.symbol_table.start_subroutine() # TODO
        # create new symbol table
        self.symbol_tables.append(symbol.SymbolTable())

        if self.current_subroutine_type == grammar.K_METHOD:
            self.symbol_table.define('this', self.class_name, grammar.arg) # TODO
            self.symbol_tables[self.last_pos()].define('this', self.class_name, grammar.arg)

        # (
        self.tokenizer.advance()
        self.checkSymbol("(")

        # parameterList ?
        self.tokenizer.advance()
        if self.tokenizer.current_value != ")":
            if self.compile_parameter_list() is not False:
                self.tokenizer.advance()
            else:
                if self.tokenizer.current_value != ')' and raise_error:
                    raise ValueError("illegal parameter list in subroutine")


        # )
        self.checkSymbol(")")

        # subroutine body
        self.tokenizer.advance()
        self.compile_subroutineBody()

        # delete symbol table
        self.symbol_tables.pop()



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

        # TODO symbol table needs to be fixed ?
        self.vm.writeFunction(self.get_vm_function_name(),
                              self.symbol_tables[self.last_pos()].varCount(grammar.keyword_2_kind[grammar.K_VAR]))

        if self.current_subroutine_type == grammar.K_METHOD:
            self.vm.writePush(grammar.K_ARG, 0) # push argument 0
            self.vm.writePop(grammar.POINTER, 0) # pop pointer 0
        elif self.current_subroutine_type == grammar.K_CONSTRUCTOR:
            # push size of object
            varCounter = 0
            for i in range(self.last_pos()):
                varCounter += self.symbol_tables[i].varCount(grammar.field)
            self.vm.writePush(grammar.CONST, varCounter)
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
            # TODO : ASK ABOUT THESE LINES
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
                isVoid = False
                if self.return_type == grammar.K_VOID:
                    isVoid = True
                self.compile_return(isVoid)
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

    # def current_is_void_or_type(self):
    #
    #     """
    #     HADAR
    #
    #     :return: true if void or type, false otherwise
    #     """
    #     return (self.tokenizer.current_value == grammar.K_VOID) or self.tokenizer.current_value in self.type_list



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
            if self.is_more_vars():
                type = self.tokenizer.current_value
                self.tokenizer.advance()
                if self.tokenizer.current_token_type == grammar.IDENTIFIER:
                    name = self.tokenizer.current_value
                    #add to symbol table
                    self.symbol_table.define(name, type, grammar.arg) # TODO
                    self.symbol_tables[self.last_pos()].define(name, type, grammar.arg)
                    self.tokenizer.advance()
                    if self.tokenizer.current_value == ',':
                        self.tokenizer.advance()
            # elif self.tokenizer.current_value == ')':
            #     more_parameters = False

            else:
                return False

        return True


    def is_more_vars(self):
        """ Checks if the type of the current type is in the type_list
        """

        return self.tokenizer.current_value != ')'


    def checkSymbol(self, symbol, raise_error=True):
        """ Check if the symbol is in the current value"""
        if self.tokenizer.current_value == symbol:
            return True
        else:
            if raise_error:
                raise ValueError("No symbol " + symbol + " found")

    def compile_if(self):
        """
        RUTHI

        Compiles an if statement, possibly with a trailing else clause.
        :return:
        """
        self.if_counter += 1

        # (
        self.tokenizer.advance()
        self.checkSymbol("(")

        # expression
        self.tokenizer.advance()
        self.compile_expression(True, True)

        # self.vm.WriteArithmetic(grammar.NOT)
        self.vm.WriteIf("IF_" + self.if_counter.__str__() + "_1")

        # )
        self.tokenizer.advance()
        self.checkSymbol(")")

        # {
        self.tokenizer.advance()
        self.checkSymbol("{")


        # TODO : CHECKNG ANOTHER VERSION OF IF
        self.vm.WriteGoto("IF_" + self.if_counter.__str__() + "_2")
        self.vm.WriteLabel("IF_" + self.if_counter.__str__() + "_1")

        # saving counter for later
        current_counter = self.if_counter

        # statements
        self.tokenizer.advance()
        self.compile_statements()

        # }
        self.checkSymbol("}")

        # (else {statement})?
        else_param = False

        if self.tokenizer.get_next()[0] == "else":
            self.tokenizer.advance()
            if self.tokenizer.current_value == "else":
                else_param = True
        if (else_param):
            # {
            self.tokenizer.advance()
            self.checkSymbol("{")

            # statement
            self.tokenizer.advance()
            self.compile_statements()

            # }
            self.checkSymbol("}")

        self.vm.WriteLabel("IF_" + current_counter.__str__() + "_2")

    def compile_while(self):
        """
        RUTHI

        Compiles a while statement.
        :return:
        """
        self.while_counter += 1

        # (
        self.tokenizer.advance()
        self.checkSymbol("(")
        # expression
        self.tokenizer.advance()

        self.vm.WriteLabel("WHILE_" + self.while_counter.__str__() + "_1")
        self.compile_expression()
        self.vm.WriteArithmetic(grammar.NOT)
        self.vm.WriteIf("WHILE_" + self.while_counter.__str__() + "_2")

        # )
        self.tokenizer.advance()
        self.checkSymbol(")")

        # {
        self.tokenizer.advance()
        self.checkSymbol("{")

        # todo : check for squaretest
        self.vm.WriteGoto("WHILE_" + self.while_counter.__str__() + "_1")
        self.vm.WriteLabel("WHILE_" + self.while_counter.__str__() + "_2")

        # statement
        self.tokenizer.advance()
        self.compile_statements()



        # }
        self.checkSymbol("}")


    def compile_let(self):
        """
        RUTHI

        Compiles a let statement.
        """

        # compile varName
        self.tokenizer.advance()
        varName = self.compile_identifier()
        position = self.last_pos()
        while self.symbol_tables[position].indexOf(varName) in [grammar.NO_INDEX, None]:
            position -= 1
        # get varName from SymbolTable
        print(varName)
        varName_index = self.get_varName_index(varName, position)
        varName_seg = self.get_varName_segment(varName, position)

        # handle array
        # [
        advance_token, is_list = False, False

        if self.tokenizer.get_next()[0] == "[":
            is_list = True
        self.tokenizer.advance()
        if is_list:
            self.compile_array_dec(varName_seg, varName_index)
            advance_token = True

        # =
        if (advance_token):
            self.tokenizer.advance()
        self.checkSymbol("=")

        # compile expression
        self.tokenizer.advance()
        if self.tokenizer.get_next()[0] == '.':
            self.compile_subroutineCall()
        else:
            self.compile_expression(True, True)

        # ;
        self.tokenizer.advance()
        self.checkSymbol(";")

        if is_list:
            self.write_push_pop_for_list()
        else: # pop value into varName

            while self.symbol_tables[position].kindOf(varName) is None:
                position -= 1
            seg = grammar.kind_2_write[self.symbol_tables[position].kindOf(varName)]
            self.vm.writePop(seg, varName_index)


    def compile_array_dec(self, var_seg, var_index):
        """

        :return:
        """
        # [
        self.checkSymbol('[')
        self.tokenizer.advance()
        self.vm.writePush(var_seg, str(var_index)) # push array pointer to stack
        self.compile_expression(True, True)
        self.tokenizer.advance()
        # ]
        self.checkSymbol(']')
        # add
        self.vm.WriteArithmetic('add')


    def write_push_pop_for_list(self):
        """
        writes to vm commands for list index
        :return:
        """
        self.vm.writePop(grammar.TEMP, grammar.TEMP_ARRAY_INDEX) # pop temp 0
        self.vm.writePop(grammar.POINTER, '1') # pop expression (from[ ]) + index to pointer
        self.vm.writePush(grammar.TEMP, grammar.TEMP_ARRAY_INDEX) # push temp 0
        self.vm.writePop(grammar.THAT, '0') # pop that 0


    def compile_array_for_expression(self, var_seg, var_index):
        """

        :return:
        """
        self.compile_array_dec(var_seg, var_index) # compiles array dec
        self.vm.writePop(grammar.POINTER, '1') # pop pointer 1
        self.vm.writePush(grammar.THAT, '0') # push that 0


    def compile_term(self, tags=True, check=False):
        """
        RUTHI

        Compiles a term. This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routine must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of [, (, or .
        suffices to distinguish between the three possibilities.
        Any other token is not part of this term and should not be advanced
        over.
        :return:
        """

        # Integer constant, String constant, keyword constant
        type = self.tokenizer.token_type()

        # integer constant
        if (type == grammar.INT_CONST):
            if check:
                return True
            self.vm.writePush(grammar.CONST, self.tokenizer.current_value)



        # keyword
        elif (type == grammar.KEYWORD and self.tokenizer.keyword() in grammar.keyword_constant):
            if check:
                return True

            self.compile_keyword()

        # subroutine call
        elif self.tokenizer.get_next()[0] == '.':
            if check:
                return True
            self.compile_subroutineCall()

        # string constant
        elif type == grammar.STRING_CONS:
            if check:
                return True
            self.compile_string_const()

        # ( expression )
        elif self.tokenizer.current_value == "(":
            if check:
                return True
            self.checkSymbol("(")
            self.tokenizer.advance()
            self.compile_expression(True, True)
            self.tokenizer.advance()
            self.checkSymbol(")")

        # unaryOp term
        elif self.tokenizer.current_value in grammar.unaryOp:
            if check:
                return True
            op = self.tokenizer.current_value
            self.checkSymbol(self.tokenizer.current_value)
            self.tokenizer.advance()
            self.compile_term()
            # op -
            if op == '-':
                self.vm.output_file.write(grammar.NEG + NEW_LINE)
            elif op == '~':
                self.vm.output_file.write(grammar.NOT + NEW_LINE)

        # varName ([ expression ])?
        elif type == grammar.IDENTIFIER:
            if check:
                return True


            # information about var
            varName = self.tokenizer.current_value
            position = self.last_pos()
            while self.symbol_tables[position].indexOf(varName) in [grammar.NO_INDEX, None]:
                position -= 1
                if position == grammar.NO_INDEX:
                    break
            varName_index = self.get_varName_index(varName, position)
            varName_segment = self.get_varName_segment(varName, position)

            # print(varName_segment + " idx: "+str(varName_index))
            if varName_index != None and self.tokenizer.get_next()[0] != '[':
                # push varName
                self.vm.writePush(varName_segment, varName_index)

            # check if array in expression
            elif varName_index != None and self.tokenizer.get_next()[0] == '[':
                self.tokenizer.advance()
                self.compile_array_for_expression(varName_segment, varName_index)

            elif (self.tokenizer.get_next()[0] == "(") or (self.tokenizer.get_next()[0] == "."):
                # subroutineCall
                self.compile_subroutineCall()

        else:
            return False

        return True

    def compile_string_const(self):
        """ Compile string constant"""
        string = self.tokenizer.current_value

        self.vm.writePush(grammar.CONST, len(string))
        self.vm.writeCall("String.new", 1)

        for i in range(len(string)):
            self.vm.writePush(grammar.CONST, ord(string[i]))
            self.vm.writeCall("String.appendChar", 2)


    def get_varName_index(self, varName, position):
        varName_index = -1
        varName_index = self.symbol_tables[position].indexOf(varName)
        return varName_index


    def get_varName_segment(self, varName, position):
        varName_kind = self.symbol_tables[position].kindOf(varName)
        segment = self.get_segment_by_kind(varName_kind)
        return segment

    def compile_keyword(self):
        """
        Compile keyword
        """
        # this
        if self.tokenizer.current_value == grammar.keyword_constant[3]:
            self.vm.writePush(grammar.POINTER, 0)
        else:
            # true, false, null
            self.vm.writePush(grammar.CONST, 0)

            if self.tokenizer.current_value == grammar.keyword_constant[0]:
                self.vm.WriteArithmetic(grammar.NOT)

    def compile_expression(self, tags=True, term_tag=False, expression_lst=False):
        """
        RUTHI

        Compiles an expression.
        :return:
        """
        expression_counter = 0

        # term
        if self.compile_term(False, True) is False:
            return False
        else:
            if expression_lst:
                return True
            self.compile_term()

        # (op term)*
        self.compile_op_term()


        return expression_counter


    def compile_op_term(self):
        op = []
        while self.tokenizer.get_next()[0] in grammar.operators:
            self.tokenizer.advance()
            op += [self.tokenizer.current_value]  # TODO why array?
            self.checkSymbol(self.tokenizer.current_value)
            self.tokenizer.advance()
            # push args for arithmetic action
            self.compile_term()

            # self.write_arithmetic_to_vm()
            if op[len(op) - 1] == "*" or op[len(op) - 1] == "/":
                self.vm.writeCall(grammar.arithmetic_dict[op[len(op) - 1]], 2)
            else:
                self.vm.WriteArithmetic(
                    grammar.arithmetic_dict[op[len(op) - 1]])


    def compile_expression_list(self):
        """
        Compiles a (possibly empty) comma separated list of expressions.
        :return:
        """
        # expression?


        args_counter = 0
        if self.compile_expression(False, False, True) is not False:
            args_counter +=1
            # (',' expression)*
            if self.tokenizer.get_next()[0] == '.':
                self.compile_subroutineCall()
            else:
                self.compile_expression(True, True)
            self.tokenizer.advance()
            while self.tokenizer.current_value == ',':
                self.checkSymbol(",")
                # expression
                self.tokenizer.advance()
                if self.tokenizer.get_next()[0] == '.':
                    self.compile_subroutineCall()
                else:
                    self.compile_expression(True, True)
                args_counter +=1
                self.tokenizer.advance()

        return args_counter


    def last_pos(self):
        """
        RUTHI

        :return: position of the last symbol table in the array
        """
        return len(self.symbol_tables) - 1

    def compile_do(self):
        """
        RUTHI

        Compiles a do statement
        :return:
        """

        # subroutineCall
        self.tokenizer.advance()
        self.compile_subroutineCall(True)

        # ;
        self.tokenizer.advance()
        self.checkSymbol(";")


    def compile_return(self,isVoid=False):
        """
        RUTHI

        Compiles a return statement.
        :return:
        """

        # expression?
        while self.tokenizer.get_next()[0] != ";":
            self.tokenizer.advance()
            self.compile_expression()

        self.tokenizer.advance()
        self.checkSymbol(";")



        # write return to vm
        if isVoid:
            self.vm.writePush(grammar.CONST, 0)
        self.vm.writeReturn()



    def compile_subroutineCall(self, do=False):
        """
        HADAR

        compiles subroutine call and writes vm code
        :return:
        """
        if self.tokenizer.token_type() == grammar.IDENTIFIER:

            # check (subroutineName ( expressionList ))
            if self.tokenizer.get_next()[0] == "(":
                self.vm.writePush(grammar.POINTER, '0') # (ball test)

                subroutine_name = self.tokenizer.current_value
                self.tokenizer.advance()
                # (
                self.tokenizer.advance()
                # expression list
                args_counter = self.compile_expression_list() + 1 # writes to vm also
                self.checkSymbol(")")

                # write to vm : call subroutine name
                self.vm.write_subroutine_call(self.class_name+"."+subroutine_name+" "+str(args_counter))

                self.vm.writePop(grammar.TEMP, '0')  # (ball test)

            # check ((className | varName).subroutineName (expressionList))
            elif self.tokenizer.get_next()[0] == ".":
                # check if current in type list
                if self.tokenizer.current_value in self.type_list:
                    type = self.tokenizer.current_value
                # else it is a var - get varType var type
                else:
                    position = self.last_pos()
                    while self.symbol_tables[position].typeOf(self.tokenizer.current_value) in [grammar.NO_INDEX, None]:
                        position -= 1
                    type = self.symbol_tables[position].typeOf(self.tokenizer.current_value)

                    varName_index = self.get_varName_index(self.tokenizer.current_value, position)
                    varName_seg = self.get_varName_segment(self.tokenizer.current_value, position)

                    # pus
                    self.vm.writePush(varName_seg, varName_index)

                # .
                self.tokenizer.advance()
                # subroutineName
                self.tokenizer.advance()
                subroutine_name = self.tokenizer.current_value
                # (
                self.tokenizer.advance()
                self.checkSymbol("(")
                self.tokenizer.advance()
                args_counter = self.compile_expression_list() # TODO : WHEN ADD 1??
                # )
                self.checkSymbol(")")
                # write to vm : call type.subroutine name
                self.vm.write_subroutine_call(type.__str__()+'.'+subroutine_name+" "+str(args_counter))

                if do:
                    self.vm.writePop(grammar.TEMP, 0)


    def get_segment_by_kind(self, kind):
        """
        return segment for
        :return:
        """
        segment = ""
        if kind == grammar.var:
            segment = grammar.LOCAL
        elif kind == grammar.arg:
            segment = grammar.K_ARG
        elif kind == grammar.field:
            segment = grammar.K_THIS
        elif kind == grammar.static:
            segment = grammar.K_STATIC
        else:
            segment = ""
        return segment










