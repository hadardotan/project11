import re


static = 1
field = 2
arg = 3
var = 4


keyword_2_kind = {'static': static, 'field' : field, 'arg' : arg, 'var' : var}




# Jack libaries
L_MATH = 'Math'
L_KEYBOARD = 'Keyboard'
L_ARRAY = 'Array'
L_MEMORY = 'Memory'
L_OUTPUT = 'Output'
L_SCREEN = 'Screen'
L_STRING = 'String'
L_SYS = 'Sys'

jack_libaries = [L_MATH, L_KEYBOARD, L_ARRAY, L_MEMORY, L_OUTPUT, L_SCREEN, L_STRING, L_SYS]

# The Jack language includes five types of terminal elements (tokens):
# KEYWORD, SYMBOL, IDENTIFIER,INT_CONST,STRING_CONS

TRUE = 1
# tokens CONSTANTS
KEYWORD = 1
SYMBOL = 2
IDENTIFIER = 3
INT_CONST = 4
STRING_CONS = 5
NO_TOKEN = -1
NO_PHRASE = -1
NO_INDEX = -1


# KEYWORD tokens
K_CLASS = 'class'
K_CONSTRUCTOR = 'constructor'
K_FUNCTION = 'function'
K_METHOD = 'method'
K_FIELD = 'field'
K_STATIC = 'static'
K_VAR = 'var'
K_INT = 'int'
K_BOOLEAN = 'boolean'
K_CHAR = 'char'
K_VOID = 'void'
K_LET = 'let'
K_DO = 'do'
K_IF = 'if'
K_ELSE = 'else'
K_WHILE = 'while'
K_RETURN = 'return'
K_TRUE = 'true'
K_FALSE = 'false'
K_NULL = 'null'
K_THIS = 'this'
K_NONE = ''
K_KEYWORD = 'keyword'
K_SYMBOL = "symbol"
K_IDENTIFIER = "identifier"
K_ARG = "argument" ## not a keyword!!!!! - kind
POINTER = 'pointer'
CONST = 'constant'
NEG = 'neg'


#Jack types
jack_types = [K_INT, K_CHAR, K_BOOLEAN]


keywords = [K_CLASS ,K_CONSTRUCTOR ,K_FUNCTION ,K_METHOD ,K_FIELD ,K_STATIC
,K_VAR ,K_INT ,K_BOOLEAN ,K_CHAR ,K_VOID ,K_LET ,K_DO ,K_IF ,K_ELSE ,K_WHILE
,K_RETURN , K_TRUE ,K_FALSE ,K_NULL ,K_THIS ,K_NONE ]

# SYMBOL tokens
symbols = ['{' , '}' , '(' , ')' , '[' , ']' , '. ' , ',' , ';' , '+' , '-' ,
          '*' , '/' , '&' , '<' , '>' , '=' , '~',"; ",", "]

STRING_RE = r'(\\"[\w\W]*\\" )'
SYMBOLS_RE = '(\\{|\\}|\\(|\\)|\\[|\\]|\\, |\\;|\\+|\\-|\\' \
             '*|\\/|\\&|\\,|\\<|\\>|\\=|\\~|\\.)'
QUOTATION_MARK = "\""

keyword_constant = ["true", "false", "null", "this"]

unaryOp = ["-", '~']

operators = ['+', '-', '*', '/', '&', '|', '<', '>', '=']

# Arithmetic operations
arithmetic_op = {'+': 'add', '-': 'sub', '*': 'Math.multiply', '/': 'Math.divide', '&': 'and', '|': 'or',
                 '<': 'lt', '>': 'gt', '=': 'eq'}

# tokens type
tokens_types = ['keyword', 'symbol', 'identifier', 'integerConstant', 'stringConstant']

# REGEX

RE_INT = r'\d+'
RE_STR = r'"[\w\W]*"'
RE_ID = r'[a-zA-Z_]+[\w]*'
RE_NEWLINE = r'/\n'
RE_WHITESPACES = r'\s' #two or more!
RE_COMMENT1 = r'//.*[\r\n]+'
RE_COMMENT2 = r'/\*[\s\S]*?\*/'
RE_COMMENT3 = r'/\**[\s\S]*?\*/'
RE_STRING = r'^"[\w\W]*"?'

RE_STRING_COMPILED = re.compile(RE_STRING)
RE_INT_COMPILED = re.compile(RE_INT)
RE_STR_COMPILED = re.compile(RE_STR)
RE_ID_COMPILED = re.compile(RE_ID)
RE_NEWLINE_COMPILED = re.compile(RE_NEWLINE)
RE_COMMENT1_COMPILED = re.compile(RE_COMMENT1)
RE_COMMENT2_COMPILED = re.compile(RE_COMMENT2)
RE_COMMENT3_COMPILED = re.compile(RE_COMMENT3)
RE_WHITESPACES_COMPILED = re.compile(RE_WHITESPACES)


