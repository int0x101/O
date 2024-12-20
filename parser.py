import ply.yacc as yacc
from lexer import tokens

precedence = (
    (
        "left",
        "EQUALS",
        "NOT_EQUALS",
        "LESS_THAN",
        "LESS_EQUAL",
        "GREATER_THAN",
        "GREATER_EQUAL",
    ),
    (
        "left",
        "PLUS",
        "MINUS",
    ),
    (
        "left",
        "TIMES",
        "DIVIDE",
    ),
    ("left", "MODULO"),
    ("right", "POWER"),
)


def p_program(p):
    """
    program : statements
    """
    p[0] = p[1]


def p_statements(p):
    """
    statements : statement
               | statements statement
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_statement(p):
    """
    statement : simple_stmt 
              | simple_stmt NEWLINE
              | compound_stmt
    """
    p[0] = p[1]


def p_simple_stmt(p):
    """
    simple_stmt : var_def
                | enum_def
                | fun_call_stmt
                | return_stmt
                | keyword_stmt
    """
    p[0] = p[1]


def p_block(p):
    """
    block : NEWLINE INDENT statements DEDENT
    """
    p[0] = p[3]


def p_compound_stmts(p):
    """
    compound_stmts : compound_stmt
                   | compound_stmts compound_stmt
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_compound_stmt(p):
    """
    compound_stmt : fun_def
    """
    p[0] = p[1]


def p_fun_def(p):
    """
    fun_def : type IDENTIFIER LPAREN RPAREN COLON block
            | type IDENTIFIER LPAREN params RPAREN COLON block
    """
    if len(p) == 7:
        p[0] = ("fun_def", p[1], p[2], [], p[6])
    else:
        p[0] = ("fun_def", p[1], p[2], p[4], p[7])


def p_params(p):
    """
    params : param
           | params COMMA param
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_param(p):
    """
    param : type IDENTIFIER
    """
    p[0] = ("param", p[1], p[2])


def p_var_def(p):
    """
    var_def : type IDENTIFIER ASSIGN expression
    """
    p[0] = ("var_def", p[1], p[2], p[4])


def p_enum_def(p):
    """
    enum_def : ENUM IDENTIFIER LBRACE enum_params RBRACE
    """
    p[0] = ("enum_def", p[2], p[4])


def p_enum_params(p):
    """
    enum_params : IDENTIFIER
                | enum_params COMMA IDENTIFIER
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_fun_call_stmt(p):
    """
    fun_call_stmt : IDENTIFIER LPAREN RPAREN
                  | IDENTIFIER LPAREN args RPAREN
    """
    if len(p) == 4:
        p[0] = ("fun_call", p[1], [])
    else:
        p[0] = ("fun_call", p[1], p[3])


def p_args(p):
    """
    args : expression
         | args COMMA expression
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_import_stmt(p):
    """
    import_stmt : IMPORT module_name
    """
    p[0] = (p[1], p[2])


def p_module_name(p):
    """
    module_name : STRINGLIT
                | module_name DOT STRINGLIT
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def log_stmt(p):
    """
    log_stmt : LOG expression
    """
    p[0] = (p[1], p[2])


def p_return_stmt(p):
    """
    return_stmt : RETURN
                | RETURN expression
    """
    p[0] = (p[1], p[2] if len(p) == 3 else None)


def p_keyword_stmt(p):
    """
    keyword_stmt : PASS
                 | SKIP
                 | ESCAPE
    """
    p[0] = (p[1],)


def p_comparision(p):
    """
    expression : expression EQUALS expression
               | expression NOT_EQUALS expression
               | expression LESS_THAN expression
               | expression LESS_EQUAL expression
               | expression GREATER_THAN expression
               | expression GREATER_EQUAL expression
    """
    p[0] = ("comparison", p[2], p[1], p[3])


def p_expression_binop(p):
    """
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression MODULO expression
               | expression POWER expression
    """
    p[0] = ("binop", p[2], p[1], p[3])


def p_expression_group(p):
    """
    expression : LPAREN expression RPAREN
    """
    p[0] = p[2]


def p_expression_identifier(p):
    """
    expression : IDENTIFIER
    """
    p[0] = ("identifier", p[1])


def p_expression(p):
    """
    expression : INTEGERLIT
               | STRINGLIT
               | BOOLEANLIT
               | DOUBLELIT
    """
    p[0] = p[1]


def p_type(p):
    """
    type : INTEGER
         | STRING
         | BOOLEAN
         | DOUBLE
    """
    p[0] = p[1]


def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()
