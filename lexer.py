import ply.lex as lex

keywords = {
    "int": "INTEGER",
    "str": "STRING",
    "bool": "BOOLEAN",
    "double": "DOUBLE",
    "import": "IMPORT",
    "class": "CLASS",
    "enum": "ENUM",
    "when": "WHEN",
    "otherwise": "OTHERWISE",
    "log": "LOG",
    "include": "INCLUDE",
    "extends": "EXTENDS",
    "self": "SELF",
    "skip": "SKIP",
    "for": "FOR",
    "in": "IN",
    "escape": "ESCAPE",
    "return": "RETURN",
    "pass": "PASS",
}

tokens = (
    "NEWLINE",
    "DOUBLELIT",
    "INTEGERLIT",
    "BOOLEANLIT",
    "STRINGLIT",
    "IDENTIFIER",
    # Terminators
    "INDENT",
    "DEDENT",
    "COMMA",
    "COLON",
    "LPAREN",
    "RPAREN",
    "LBRACKET",
    "RBRACKET",
    "LBRACE",
    "RBRACE",
    # Symbols
    "EQUALS",
    "NOT_EQUALS",
    "LESS_THAN",
    "LESS_EQUAL",
    "GREATER_THAN",
    "GREATER_EQUAL",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "POWER",
    "MODULO",
    "ASSIGN",
    "DOT",
) + tuple(keywords.values())

t_DOT = r"\."
t_COMMA = r","
t_COLON = r":"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"

t_ASSIGN = r"="
t_EQUALS = r"=="
t_NOT_EQUALS = r"!="
t_LESS_THAN = r"<"
t_LESS_EQUAL = r"<="
t_GREATER_THAN = r">"
t_GREATER_EQUAL = r">="

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_POWER = r"\*\*"
t_MODULO = r"%"

indentation_stack = [0]

def t_COMMENT(t):
    r'(\#!).*'
    pass


def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    t.lexer.linestart = t.lexer.lexpos
    return t


def t_eof(t):
    print(indentation_stack)
    if 0 < indentation_stack[-1]:
        indentation_stack.pop()
        t.value = 0
        t.type = "DEDENT"
        return t
    pass


def t_DEDENT(t):
    r"(?<=\n)\S"
    t.value = len(t.value)
    while indentation_stack[-1] > 0:
        indentation_stack.pop()
        t.type = "DEDENT"
        return t
    pass


def t_whitespaces(t):
    r"(?<=\n)[\s\t]+|^[\s\t]+"
    spaces = len(t.value)
    if spaces > indentation_stack[-1]:
        indentation_stack.append(spaces)
        t.value = spaces
        t.type = "INDENT"
        return t
    elif spaces < indentation_stack[-1]:
        while indentation_stack[-1] > spaces and len(indentation_stack) > 1:
            indentation_stack.pop()
        t.value = spaces
        t.type = "DEDENT"
        return t
    pass


def t_DOUBLELIT(t):
    r"\d+\.\d+"
    return t


def t_INTEGERLIT(t):
    r"\d+"
    return t


def t_BOOLEANLIT(t):
    r"True|False"
    return t


def t_STRINGLIT(t):
    r'"([^\\\n]|(\\.))*?"'
    t.value = t.value[1:-1]


def t_IDENTIFIER(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = keywords.get(t.value, "IDENTIFIER")
    return t


def t_SKIP_WHITESPACES(t):
    r"[ \t]+"
    pass


def t_error(t):
    raise Exception(
        "Illegal character '%s' on line %d, column %d"
        % (t.value[0], t.lexer.lineno, t.lexer.lexpos - t.lexer.linestart + 1)
    )


lexer = lex.lex()
