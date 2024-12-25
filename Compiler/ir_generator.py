import llvmlite.ir as ir
import llvmlite.binding as llvm
from llvmlite.binding import get_default_triple


from .scope import ScopeStack


class IRGenerator(ScopeStack):
    def __init__(self):
        self.module: ir.Module = ir.Module(name="module")
        self.module.triple = get_default_triple()
        self.builder: ir.builder = None
        self.func: ir.Function = None
        self.typemap = {
            'int': ir.IntType(32),
            'double': ir.DoubleType(),
            'void': ir.VoidType(),
            'bool': ir.IntType(1),
            'str': ir.IntType(8).as_pointer(),
        }
        super().__init__()

    def generate(self, ast):
        self.visit(ast)
        return str(self.module)

    def visit(self, node):
        method_name = f"visit_{node[0]}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for child in node[1]:
            if isinstance(child, tuple):
                self.visit(child)

    def visit_program(self, node):
        ftype = ir.FunctionType(ir.VoidType(), [])
        self.func = ir.Function(self.module, ftype, name="main",)

        block = self.func.append_basic_block(name="entry")
        builder = ir.IRBuilder(block)
        self.builder = builder

        self.generic_visit(node)
        builder.ret_void()

    def visit_var_def(self, node):
        type, name, value = node[1:]
        try:
            var_type = self.typemap[type]
        except KeyError:
            raise TypeError(f"Unknown type {type}")
        var_value = self.visit(value)
        var_ptr = self.builder.alloca(var_type, name=name)
        self.builder.store(var_value, var_ptr)
        self.current_scope()[name] = var_ptr

    def visit_enum_def(self, node):
        name, members = node[1:]
        enum_dict = {}
        for i, member in enumerate(members):
            enum_type = ir.IntType(32)
            enum_value = ir.Constant(enum_type, i)
            enum_dict[member] = enum_value
        self.current_scope()[name] = enum_dict

    def visit_class_def(self, node):
        decorators, name, extends, body = node[1:]
        class_type = ir.global_context.get_identified_type(name)
        self.current_scope()[name] = class_type

        self.enter_scope()
        for child in body:
            self.visit(child)
        self.exit_scope()
    

    def visit_fun_def(self, node):
        ret_type, name, params, body = node[1:]
        param_types = [self.typemap[param[0]] for param in params]
        func_type = ir.FunctionType(self.typemap[ret_type], param_types)
        func = ir.Function(self.module, func_type, name=name)

        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        self.enter_scope()
        for i, param in enumerate(params):
            param_name = param[1]
            var_ptr = self.builder.alloca(param_types[i], name=param_name)
            self.builder.store(func.args[i], var_ptr)
            self.current_scope()[param_name] = var_ptr

        for child in body:
            self.visit(child)
        self.exit_scope()

    def visit_assignment(self, node):
        name, value = node[1:]
        var_ptr = self.resolve(name)
        var_value = self.visit(value)
        self.builder.store(var_value, var_ptr)

    def visit_return(self, node):
        try:
            value = self.visit(node[1])
            self.builder.ret(value)
        except IndexError:
            self.builder.ret_void()

    def visit_binop(self, node):
        op, left, right = node[1:]
        left = self.visit(left)
        right = self.visit(right)

        match op:
            case '+':
                return self.builder.add(left, right)
            case '-':
                return self.builder.sub(left, right)
            case '*':
                return self.builder.mul(left, right)
            case '/':
                return self.builder.sdiv(left, right)
            case '%':
                return self.builder.srem(left, right)
            case '**':
                return self.builder.fmul(left, right)
            case _:
                raise ValueError(f"Unknown binary operator {op}")

    def visit_comparison(self, node):
        op, left, right = node[1:]
        left = self.visit(left)
        right = self.visit(right)

        match op:
            case '==':
                return self.builder.icmp_signed('==', left, right)
            case '!=':
                return self.builder.icmp_signed('!=', left, right)
            case '<':
                return self.builder.icmp_signed('<', left, right)
            case '<=':
                return self.builder.icmp_signed('<=', left, right)
            case '>':
                return self.builder.icmp_signed('>', left, right)
            case '>=':
                return self.builder.icmp_signed('>=', left, right)
            case _:
                raise ValueError(f"Unknown comparison operator {op}")

    def visit_identifier(self, node):
        var_ptr = self.resolve(node[1])
        return self.builder.load(var_ptr)

    def visit_integer(self, node):
        return ir.Constant(ir.IntType(32), int(node[1]))

    def visit_double(self, node):
        return ir.Constant(ir.DoubleType(), float(node[1]))

    def visit_string(self, node):
        return ir.Constant(ir.IntType(8).as_pointer(), node[1])

    def visit_boolean(self, node):
        value = 1 if node[1] == 'True' else 0
        return ir.Constant(ir.IntType(1), value)

    def visit_when_stmts(self, node):
        for when_stmt in node[1:]:
            self.visit(when_stmt)

    def visit_when(self, node):
        condition, body = node[1:]
        condition = self.visit(condition)

        with self.builder.if_then(condition):
            for child in body:
                self.visit(child)
