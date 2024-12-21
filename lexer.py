import re
import ply.lex as lex

# Keywords
keywords = {
    # Data types
    "int": "INTEGER",
    "str": "STRING",
    "bool": "BOOLEAN",
    "double": "DOUBLE",

    # Declarations
    "import": "IMPORT",
    "class": "CLASS",
    "enum": "ENUM",

    # Control flow
    "when": "WHEN",
    "otherwise": "OTHERWISE",
    "for": "FOR",
    "in": "IN",
    "switch": "SWITCH",
    "case": "CASE",
    "try": "TRY",
    "except": "EXCEPT",

    # Functions and methods
    "log": "LOG",
    "include": "INCLUDE",
    "extends": "EXTENDS",
    "self": "SELF",
    "async": "ASYNC",
    "escape": "ESCAPE",
    "return": "RETURN",
    "pass": "PASS",
    "skip": "SKIP",
}

# Token list
tokens = (
    # Literals
    "DOUBLELIT",
    "INTEGERLIT",
    "BOOLEANLIT",
    "STRINGLIT",
    "TEMPLATE_STRING",
    "IDENTIFIER",

    # Indentation
    "INDENT",
    "DEDENT",

    # Delimiters
    "COMMA",
    "COLON",
    "LPAR",
    "RPAR",
    "LSQB",
    "RSQB",
    "LBRACE",
    "RBRACE",
    "DOT",
    "AT",

    # Operators
    "EQEQUAL",
    "NOT_EQEQUAL",
    "LESS",
    "LESSEQUAL",
    "GREATER",
    "GREATEREQUAL",
    "PLUS",
    "MINUS",
    "STAR",
    "SLASH",
    "DOUBLESTAR",
    "PERCENT",
    "EQUAL",
    "VBAR",
    "DOUBLE_VBAR",
    "DOUBLE_AMP",
    "EXCLAMATION",
    "QUESTION",
    "ELLIPSIS",

    # Keywords
    "NEWLINE",
) + tuple(keywords.values())

# Terminators
t_DOT = r"\."
t_COMMA = r","
t_COLON = r":"
t_LPAR = r"\("
t_RPAR = r"\)"
t_LSQB = r"\["
t_RSQB = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_AT = r"@"

t_EQUAL = r"="
t_EQEQUAL = r"=="
t_NOT_EQEQUAL = r"!="
t_LESS = r"<"
t_LESSEQUAL = r"<="
t_GREATER = r">"
t_GREATEREQUAL = r">="
t_DOUBLE_VBAR = r"\|\|"
t_DOUBLE_AMP = r"&&"
t_PLUS = r"\+"
t_MINUS = r"-"
t_STAR = r"\*"
t_SLASH = r"/"
t_DOUBLESTAR = r"\*\*"
t_PERCENT = r"%"
t_VBAR = r"\|"
t_EXCLAMATION = r"!"
t_QUESTION = r"\?"
t_ELLIPSIS = r"\.\.\."

indentation_stack = [0]


def t_COMMENT(t):
    r"\#.*"
    pass


def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    t.lexer.linestart = t.lexer.lexpos
    return t


def t_whitespaces(t):
    r"(?<=\n)[ \t]+"
    t.value = len(t.value) - 1
    if t.value > indentation_stack[-1]:
        indentation_stack.append(t.value)
        t.type = "INDENT"
        return t
    elif t.value < indentation_stack[-1]:
        while indentation_stack[-1] > t.value and len(indentation_stack) > 1:
            t.lexer.lexpos -= 1
            t.value = indentation_stack[-1]
            indentation_stack.pop()
            t.type = "DEDENT"
        return t
    return None


def t_DOUBLELIT(t):
    r"\d+\.\d+"
    return t


def t_INTEGERLIT(t):
    r"\d+"
    return t


def t_BOOLEANLIT(t):
    r"True|False"
    return t


def t_TEMPLATE_STRING(t):
    r't"([^\\\n]|(\\.))*?"'
    t.value = t.value[2:-1]
    return t


def t_STRINGLIT(t):
    r'"([^\\\n]|(\\.))*?"'
    t.value = t.value[1:-1]
    return t


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


def sanitize(data):
    multiple_newlines_regex = r"\n+"
    sanitized_newline = "\n "
    return re.sub(multiple_newlines_regex, sanitized_newline, data.lstrip())


lexer = lex.lex()
input_function = lexer.input
lexer.input = lambda data: input_function(sanitize(data))
