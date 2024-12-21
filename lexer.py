import re
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
    "switch": "SWITCH",
    "case": "CASE",
    "async": "ASYNC",
    "escape": "ESCAPE",
    "return": "RETURN",
    "pass": "PASS",
    "try": "TRY",
    "except": "EXCEPT",
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
    "AT",
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
t_AT = r"@"

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
