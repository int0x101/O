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
                  | class_def
                  | when_stmt
                  | for_stmt
                  | switch_stmt
    """
    p[0] = p[1]


def p_block(p):
    """
    block : NEWLINE INDENT statements DEDENT
    """
    p[0] = p[3]


def p_decorators(p):
    """
    decorators : decorator NEWLINE
               | decorator decorators
    """
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_decorator(p):
    """
    decorator : AT IDENTIFIER
              | AT IDENTIFIER LPAREN RPAREN
              | AT IDENTIFIER LPAREN args RPAREN
    """
    p[0] = ("decorator", p[2])


def p_class_def(p):
    """
    class_def : decorators class_def_raw
              | class_def_raw
    """
    if len(p) == 3:
        fun = list(p[2])
        fun[1] = p[1]
        p[0] = tuple(fun)
    else:
        p[0] = p[1]


def p_class_def_raw(p):
    """
    class_def_raw : CLASS IDENTIFIER COLON block
                  | CLASS IDENTIFIER EXTENDS IDENTIFIER COLON block
    """
    if len(p) == 5:
        p[0] = ("class_def", [], p[1], [], p[4])
    else:
        p[0] = ("class_def", [], p[1], [p[4]], p[6])


def p_fun_def(p):
    """
    fun_def : decorators fun_def_raw
            | fun_def_raw
    """
    if len(p) == 3:
        fun = list(p[2])
        fun[1] = p[1]
        p[0] = tuple(fun)
    else:
        p[0] = p[1]


def p_fun_def_raw(p):
    """
    fun_def_raw : type IDENTIFIER LPAREN RPAREN COLON block
                | type IDENTIFIER LPAREN params RPAREN COLON block
                | ASYNC fun_def_raw
    """
    if len(p) == 3:
        p[0] = ("async", p[2])
    if len(p) == 7:
        p[0] = ("fun_def", [], p[1], p[2], [], p[6])
    else:
        p[0] = ("fun_def", [], p[1], p[2], p[4], p[7])


def p_params(p):
    """
    params :
           | param
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


def p_when_stmt(p):
    """
    when_stmt : when_block
               | when_stmt when_block
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_when_block(p):
    """
    when_block : WHEN expression COLON block otherwise_block
              | WHEN expression COLON block
    """
    if len(p) == 5:
        p[0] = ("when", p[2], p[4], None)
    else:
        p[0] = ("when", p[2], p[4], p[5])


def p_otherwise_block(p):
    """
    otherwise_block : OTHERWISE COLON block
    """
    p[0] = ("otherwise", p[3])


def p_for_stmt(p):
    """
    for_stmt : FOR param IN expression COLON block
    """
    p[0] = ("for_stmt", p[2], p[4], p[6])


def p_switch_stmt(p):
    """
    switch_stmt : SWITCH expression COLON switch_cases DEDENT
                | SWITCH expression COLON switch_cases
    """
    p[0] = ("switch_stmt", p[2], p[4])


def p_switch_cases(p):
    """
    switch_cases : NEWLINE INDENT switch_case
                 | switch_cases switch_case
    """
    if len(p) == 4:
        p[0] = [p[3]]
    else:
        p[0] = p[1] + [p[2]]


def p_switch_case(p):
    """
    switch_case : CASE expression COLON NEWLINE INDENT statements DEDENT
    """
    p[0] = ("case", p[2], p[6])


def p_var_def(p):
    """
    var_def : type IDENTIFIER
            | type IDENTIFIER ASSIGN expression
    """
    if len(p) == 3:
        p[0] = (
            "var_def",
            p[1],
            p[2],
        )
    else:
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


def p_lambdef(p):
    """
    lambdef : params ASSIGN GREATER_THAN expression
    """
    p[0] = ("lambda", p[1], p[4])


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


def p_expression_literals(p):
    """
    expression : INTEGERLIT
               | STRINGLIT
               | BOOLEANLIT
               | DOUBLELIT
    """
    p[0] = p[1]


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


def p_expression_comparision(p):
    """
    expression : expression EQUALS expression
               | expression NOT_EQUALS expression
               | expression LESS_THAN expression
               | expression LESS_EQUAL expression
               | expression GREATER_THAN expression
               | expression GREATER_EQUAL expression
    """
    p[0] = ("comparison", p[2], p[1], p[3])


def p_expression_stmt(p):
    """
    expression : lambdef
    """
    p[0] = p[1]


def p_expression_identifier(p):
    """
    expression : IDENTIFIER
    """
    p[0] = ("identifier", p[1])


def p_type(p):
    """
    type : primitive_types
         | composed_types
    """
    p[0] = p[1]


def p_primitive_types(p):
    """
    primitive_types : INTEGER
                    | STRING
                    | BOOLEAN
                    | DOUBLE
    """
    p[0] = p[1]


def p_composed_types(p):
    """
    composed_types : array_type
                   | object_type
    """
    p[0] = p[1]


def p_array_type(p):
    """
    array_type : type LBRACKET RBRACKET
    """
    p[0] = f"{p[1]}[]"


def p_array_literals(p):
    """
    expression : LBRACKET RBRACKET
               | LBRACKET args RBRACKET
    """
    if len(p) == 3:
        p[0] = ("array_literal", [])
    else:
        p[0] = ("array_literal", p[2])


def p_object_type(p):
    """
    object_type : LBRACE ktype IDENTIFIER COLON type RBRACE
    """
    p[0] = "{%s: %s}" % (p[2], p[5])


def p_ktype(p):
    """
    ktype : INTEGER
          | STRING
    """
    p[0] = p[1]


def p_object_literals(p):
    """
    expression : LBRACE RBRACE
               | LBRACE kvpairs RBRACE
    """
    if len(p) == 3:
        p[0] = ("object_literal", {})
    else:
        p[0] = ("object_literal", p[2])


def p_kvpairs(p):
    """
    kvpairs : kvpair
            | kvpairs COMMA kvpair
    """
    if len(p) == 2:
        p[0] = {p[1][0]: p[1][1]}
    else:
        p[0] = {**p[1], p[3][0]: p[3][1]}


def p_kvpair(p):
    """
    kvpair : kv_key COLON expression
    """
    p[0] = (p[1], p[3])


def p_kv_key(p):
    """
    kv_key : INTEGERLIT
           | STRINGLIT
           | DOUBLELIT
    """
    p[0] = p[1]


def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()
