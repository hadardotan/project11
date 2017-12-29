# This class writes VM commands into a file. It encapsulates the VM
# command syntax.

class VMwriter(object):
    """
    Emits VM commands into a file
    """
    def __init__(self, output_file):
        """
        Creates a new file and prepares it for writing VM commands
        :param output_file:
        """
        self.output_file = output_file #already opened in main


    def writePush(self, segment, index):
        """
        Writes a VM push command
        :param segment:CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER or TEMP
        :param index:int
        :return:
        """

        self.output_file.write("push "+segment+" "+str(index)+"\n" )

    def writePop(self, segment, index):
        """
        Writes a VM pop command
        :param segment:CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER or TEMP
        :param index:int
        :return:
        """
        self.output_file.write("pop "+ str(segment) +" "+ str(index) +"\n" )

    def WriteArithmetic(self, command):
        """
        Writes a VM arithmetic command
        :param command:ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT
        :return:
        """
        self.output_file.write(command + "\n")

    def WriteLabel(self, label):
        """
        Writes a VM label command

        :param label: string
        :return:
        """
        self.output_file.write("label " + label + "\n")


    def WriteGoto(self, label):
        """

        :param label:
        :return:
        """
        self.output_file.write("goto " + label + "\n")

    def WriteIf(self, label):
        """
        Writes a VM If-goto command
        :param label:
        :return:
        """
        self.output_file.write("if-goto " + label + "\n")

    def writeCall(self, name, n):
        """
        Writes a VM call command

        :param name: string
        :param n: num of args
        :return:
        """
        self.output_file.write("call " + name + " " + str(n) + "\n")

    def writeFunction(self, name, n):
        """
        Writes a VM function command
        :param name:
        :param n: num of locals
        :return:
        """
        self.output_file.write("function " + name + " " + str(n) + "\n")

    def writeReturn(self):
        """
        Writes a VM return command
        :return:
        """
        self.output_file.write("return" + "\n")

    def write_push_var(self, var):
        self.output_file.write("push " +var+ "\n")


    def write_subroutine_call(self, subroutine_name):
        """
        calling subroutine with no args
        :param subroutine_name:
        :return:
        """
        self.output_file.write("call " + subroutine_name + "\n")


    def close(self):
        """
        Closes the output file
        :return:
        """
        self.output_file.close()

