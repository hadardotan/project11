import sys, os, os.path, glob, re
from Compiler.CompilationEngine import CompilationEngine


def analyze(files_to_process):
    """
    for each jack file in files_to_process:

    - Create a tokenizer from the Xxx.jack file
    - Create a VM-writer into the Xxx.vm file
    - Compile(INPUT: tokenizer, OUTPUT: VM-writer)
    :param files_to_process: paths of files to process
    :return:
    """
    dir_classes = []
    for input_file_name in files_to_process:
        file_name = os.path.splitext(input_file_name)[0]
        # TODO : CHECK WITH LINUX SLASH !!!!!
        last_slash = file_name.rfind('\\')
        file_class_name = file_name[last_slash+1:]
        dir_classes += [file_class_name]

    for input_file_name in files_to_process:
        file_name = os.path.splitext(input_file_name)[0]
        output_file_name = file_name + ".vm"
        input_file = open(input_file_name,'r')
        output_file = open(output_file_name,'w')

        compiler = CompilationEngine(input_file, output_file, dir_classes)


def main(path):
    """
    The program receives a name of a file or a directory, and compiles
     the file, or all the Jack files in this directory.
    For each Xxx.jack file, it creates a Xxx.vm file in the same directory.

    :return:
    """
    files_to_process =[]
    if os.path.isfile(path):
        files_to_process = [path]

    elif os.path.isdir(path):
        files_to_process = [os.path.join(path, f) for f in os.listdir(path) if
                            f.endswith(".jack")]

    analyze(files_to_process)




if __name__ == "__main__":
    main(sys.argv[1])



main("C:\nand\nand2tetris\projects\11\Pong")