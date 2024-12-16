import ply.yacc as yacc
from lexer import tokens

precedence = (
    ("left", "EQUALS",
     "NOT_EQUALS",
     "LESS_THAN",
     "LESS_EQUAL",
     "GREATER_THAN",
     "GREATER_EQUAL",),
    ("left",
     "PLUS",
     "MINUS",), ("left",
                 "TIMES",
                 "DIVIDE",),
    ("left", "MODULO"),
    ("right", "POWER")
)


def p_program(p):
    """
    program : statements
    """
    p[0] = p[1]


def p_statements(p):
    """
    statements : statement
               | statements NEWLINE statement
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_statement(p):
    """
    statement : var_def
              | fun_def
              | class_def
              | return_stmt
              | empty
    """
    p[0] = p[1]


def p_var_def(p):
    """
    var_def : type IDENTIFIER
            | type IDENTIFIER ASSIGN expression
    """
    if len(p) == 3:
        p[0] = ("var_def", p[1], p[2])
    else:
        p[0] = ("var_def", p[1], p[2], p[4])


def p_fun_def(p):
    """
    fun_def : type IDENTIFIER LPAREN RPAREN COLON compound_statement
            | type IDENTIFIER LPAREN params RPAREN COLON compound_statement
    """
    if len(p) == 7:
        p[0] = ("fun_def", p[1], p[2], [], p[6])
    else:
        p[0] = ("fun_def", p[1], p[2], p[4], p[7])


def p_class_def(p):
    """
    class_def : CLASS IDENTIFIER COLON compound_statements
    """
    p[0] = ("class_def", p[2], p[4])


def p_compound_statements(p):
    """
    compound_statements : NEWLINE INDENT statements
                        | compound_statements NEWLINE statements
                        |
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + [p[3]]


def p_compound_statement(p):
    """
    compound_statement : NEWLINE INDENT statements
    """
    p[0] = p[3]


def p_expression_binop(p):
    """
    expression : expression PLUS expression
               | expression MINUS expression    
               | expression TIMES expression    
               | expression DIVIDE expression    
               | expression POWER expression    
               | expression MODULO expression    
    """
    p[0] = ("binop", p[2], p[1], p[3])


def p_expression_comparison(p):
    """
    expression : expression EQUALS expression
               | expression NOT_EQUALS expression
               | expression LESS_THAN expression
               | expression LESS_EQUAL expression
               | expression GREATER_THAN expression
               | expression GREATER_EQUAL expression
    """
    p[0] = ("comparison", p[2], p[1], p[3])


def p_expression(p):
    """
    expression : INTEGERLIT
               | STRINGLIT
               | BOOLEANLIT
               | FLOATLIT
    """
    p[0] = p[1]


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
    p[0] = (p[1], p[2])


def p_return_stmt(p):
    """
    return_stmt : RETURN
                | RETURN expression
    """
    if len(p) == 2:
        p[0] = (p[1], None)
    else:
        p[0] = (p[1], p[2])


def p_type(p):
    """
    type : INTEGER
         | STRING
         | BOOLEAN
         | FLOAT
    """
    p[0] = p[1]


def p_empty(p):
    """
    empty :
    """
    p[0] = None


def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()
