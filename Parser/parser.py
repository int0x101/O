import ply.yacc as yacc
from Parser.lexer import tokens

precedence = (
    ("left", "EQEQUAL", "NOT_EQEQUAL", "LESS", "LESSEQUAL", "GREATER", "GREATEREQUAL"),
    ("left", "PLUS", "MINUS"),
    ("left", "STAR", "SLASH"),
    ("left", "PERCENT"),
    ("right", "DOUBLESTAR"),
    ("left", "DOUBLE_VBAR"),
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
                | assignment
                | enum_def
                | fun_call_stmt
                | return_stmt
                | keyword_stmt
                | import_stmt
                | expression
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
                  | when_stmts
                  | for_stmt
                  | switch_stmt
                  | try_stmt
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
              | AT IDENTIFIER LPAR RPAR
              | AT IDENTIFIER LPAR args RPAR
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
    if len(p) <= 6:
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
    fun_def_raw : type IDENTIFIER LPAR RPAR COLON block
                | type IDENTIFIER LPAR params RPAR COLON block
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


def p_when_stmts(p):
    """
    when_stmts : when_stmt
               | when_stmt otherwise_block
               | when_stmts when_stmt
               | when_stmts when_stmt otherwise_block
    """
    if len(p) == 2:
        p[0] = ("when_stmts", p[1])
    elif len(p) == 3:
        if p[2][0] == "otherwise":
            p[0] = ("when_stmts", p[1]) + (p[2],)
        else:
            p[0] = ("when_stmts", p[1][1]) + (p[2],)
    else:
        p[0] = ("when_stmts", p[1][1]) + (p[2], p[3])


def p_when_stmt(p):
    """
    when_stmt : WHEN expression COLON block
    """
    p[0] = ("when", p[2], p[4])


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
            | type IDENTIFIER EQUAL expression
    """
    if len(p) == 3:
        p[0] = ("var_def", p[1], p[2])
    else:
        p[0] = ("var_def", p[1], p[2], p[4])


def p_assignment(p):
    """
    assignment : IDENTIFIER assignment_op_sign expression
    """
    p[0] = ("assignment", p[2], p[1], p[3])


def p_assignment_op_sign(p):
    """
    assignment_op_sign : EQUAL
                        | PLUS_EQUAL
                        | MINUS_EQUAL
                        | STAR_EQUAL
                        | SLASH_EQUAL
                        | PERCENT_EQUAL
                        | DOUBLESTAR_EQUAL
    """
    p[0] = p[1]


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
    lambdef : params EQUAL GREATER expression
    """
    p[0] = ("lambda", p[1], p[4])


def p_fun_call_stmt(p):
    """
    fun_call_stmt : IDENTIFIER LPAR RPAR
                  | IDENTIFIER LPAR args RPAR
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


def p_expression_integer_literal(p):
    """expression : INTEGERLIT"""
    p[0] = ("integer", p[1])


def p_expression_double_literal(p):
    """expression : DOUBLELIT"""
    p[0] = ("double", p[1])


def p_expression_boolean_literal(p):
    """expression : BOOLEANLIT"""
    p[0] = ("boolean", p[1])


def p_expression_string_literal(p):
    """expression : STRINGLIT"""
    p[0] = ("string", p[1])


def p_expression_binop(p):
    """
    expression : expression PLUS expression
               | expression MINUS expression
               | expression STAR expression
               | expression SLASH expression
               | expression PERCENT expression
               | expression DOUBLESTAR expression
    """
    p[0] = ("binop", p[2], p[1], p[3])


def p_expression_group(p):
    """
    expression : LPAR expression RPAR
    """
    p[0] = p[2]


def p_expression_comparision(p):
    """
    expression : expression EQEQUAL expression
               | expression NOT_EQEQUAL expression
               | expression LESS expression
               | expression LESSEQUAL expression
               | expression GREATER expression
               | expression GREATEREQUAL expression
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


def p_expression_string_template(p):
    """
    expression : TEMPLATE_STRING
    """
    p[0] = ("template_string", p[1])


def p_expression_inline_condition(p):
    """
    expression : expression QUESTION expression EXCLAMATION expression
    """
    p[0] = ("inline_condition", p[1], p[3], p[5])


def p_expression_logical_or(p):
    """
    expression : expression DOUBLE_VBAR expression
    """
    p[0] = ("logical_or", p[1], p[3])


def p_expression_logical_and(p):
    """
    expression : expression DOUBLE_AMP expression
    """
    p[0] = ("logical_and", p[1], p[3])


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
    array_type : type LSQB RSQB
    """
    p[0] = f"{p[1]}[]"


def p_array_literals(p):
    """
    expression : LSQB RSQB
               | LSQB args RSQB
    """
    if len(p) == 3:
        p[0] = ("array_literal", [])
    else:
        p[0] = ("array_literal", p[2])


def p_array_range(p):
    """
    expression : LSQB expression ELLIPSIS expression RSQB
    """
    p[0] = ("array_range", p[2], p[4])


def p_array_comprehension(p):
    """
    expression : LSQB expression FOR param IN expression RSQB
               | LSQB expression FOR param IN expression WHEN expression RSQB
    """
    if len(p) == 8:
        p[0] = ("array_comprehension", p[2], p[4], p[6])
    else:
        p[0] = ("array_comprehension", p[2], p[4], p[6], p[8])


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
               | LBRACE unpacked_kvpairs RBRACE
    """
    if len(p) == 3:
        p[0] = ("object_literal", {})
    else:
        p[0] = ("object_literal", p[2])


def p_unpacked_kvpairs(p):
    """
    unpacked_kvpairs : unpacked_kvpair
                     | unpacked_kvpairs COMMA unpacked_kvpair
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_unpacked_kvpair(p):
    """
    unpacked_kvpair : DOUBLESTAR IDENTIFIER
                    | kvpair
    """
    if len(p) == 3:
        p[0] = ("unpack", p[2])
    else:
        p[0] = p[1]


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
    p[0] = ("keypair", p[1], p[3])


def p_kv_key(p):
    """
    kv_key : INTEGERLIT
           | STRINGLIT
           | DOUBLELIT
    """
    p[0] = p[1]


def p_try_stmt(p):
    """
    try_stmt : TRY COLON block except_blocks
    """
    p[0] = ("try", p[3], p[4])


def p_except_blocks(p):
    """
    except_blocks : except_block
                  | except_blocks except_block
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_except_block(p):
    """
    except_block : EXCEPT COLON block
                 | EXCEPT IDENTIFIER COLON block
    """
    if len(p) == 4:
        p[0] = ("except", None, p[3])
    else:
        p[0] = ("except", p[2], p[4])


def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")


def ensure_newline_at_end(data):
    if not data.endswith("\n"):
        return data + "\n"
    return data


parser = yacc.yacc()
parser_function = parser.parse
parser.parse = lambda data: parser_function(ensure_newline_at_end(data))
