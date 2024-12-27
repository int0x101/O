import llvmlite.ir as ir
from llvmlite.binding import get_default_triple

from .scope import ScopeStack


class IRGenerator:
    def __init__(self):
        self.module: ir.Module = ir.Module(name="module")
        self.module.triple = get_default_triple()
        self.builder: ir.IRBuilder = None
        self.func: ir.Function = None
        self.current_instance: ir.AllocaInstr = None
        self.switch_block: ir.SwitchInstr = None
        self.scope = ScopeStack()
        self.classes = {}

    def generate(self, ast):
        self.visit(ast)
        return str(self.module)

    def visit(self, node):
        method_name = f"visit_{node[0]}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for child in node if isinstance(node, list) else node[1]:
            if isinstance(child, tuple):
                self.visit(child)

    def visit_var_def(self, node):
        var_type, var_name, value = node[1:]
        initial_value = self.visit(value)
        ir_type = self._get_ir_type(var_type)
        ptr = self.builder.alloca(ir_type, name=var_name)
        self.builder.store(initial_value, ptr=ptr)
        self.scope.define(var_name, ptr)

    def visit_fun_def(self, node):
        modifiers, rtype, name, params, body = node[1:]
        param_types = [self._get_ir_type(param[0]) for param in params]
        return_type_ir = self._get_ir_type(rtype)
        func_type = ir.FunctionType(return_type_ir, param_types)
        self.func = ir.Function(self.module, func_type, name=name)
        block = self.func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(block)
        self.scope.enter()
        for idx, (param_type, param_name) in enumerate(params):
            ptr = self.builder.alloca(self._get_ir_type(param_type), param_name)
            self.builder.store(self.func.args[idx], ptr)
            self.scope.define(param_name, ptr)
        self.visit(body)
        self.scope.leave()
        if not self.builder.block.is_terminated:
            if isinstance(return_type_ir, ir.VoidType):
                self.builder.ret_void()
            else:
                self.builder.ret(self._get_default_value(return_type_ir))

    def visit_class_def(self, node):
        modifiers, name, base_class, body = node[1:]
        class_type = ir.global_context.get_identified_type(name)
        fields = [(field[2], self._get_ir_type(field[1])) for field in body if field[0] == 'var_def']
        class_type.set_body(*[field[1] for field in fields])
        self.classes[name] = {
            "type": class_type,
            "fields": {field[0]: idx for idx, field in enumerate(fields)}
        }
        for item in body:
            if item[0] == 'class_ctor_def':
                self._generate_constructor(name, class_type, item)
        for item in body:
            if item[0] == 'fun_def':
                self._generate_method(name, class_type, item)

    def visit_assignment(self, node):
        op, var_name, expr = node[1:]
        if self.current_instance:
            class_name = self.current_instance.type.pointee.name
            field_index = self._get_field_index(class_name, var_name)
            field_ptr = self.builder.gep(self.current_instance, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), field_index)])
            expr_value = self.visit(expr)
            self.builder.store(expr_value, field_ptr)
        else:
            var_alloca = self.scope.resolve(var_name)
            if not var_alloca:
                raise Exception(f"Undefined variable: {var_name}")
            expr_value = self.visit(expr)
            if op == "=":
                self.builder.store(expr_value, var_alloca)
            else:
                current_value = self.builder.load(var_alloca, var_name)
                op_name = self._get_op_method(op[:-1])
                method = getattr(self.builder, op_name)
                if method:
                    result = method(current_value, expr_value, f"{var_name}_{op_name}")
                    self.builder.store(result, var_alloca)

    def visit_fun_call(self, node):
        func_name, args = node[1:]
        if self.current_instance:
            class_name = self.current_instance.type.pointee.name
            func = self.module.get_global(f"{class_name}_{func_name}")
            if not func:
                raise Exception(f"Undefined method: {func_name} in class {class_name}")
            arg_values = [self.visit(arg) for arg in args]
            return self.builder.call(func, [self.current_instance] + arg_values, name=f"{func_name}_call")
        else:
            func = self.module.get_global(func_name)
            if not func or not isinstance(func, ir.Function):
                raise Exception(f"Undefined function: {func_name}")
            arg_values = [self.visit(arg) for arg in args]
            return self.builder.call(func, arg_values, name=f"{func_name}_call")

    def visit_when_stmts(self, node):
        stmts = node[1]
        self.visit(stmts)

    def visit_when(self, node):
        cond, stmts = node[1:]
        cond = self.visit(cond)
        with self.builder.if_then(cond):
            self.visit(stmts)

    def visit_otherwise(self, node):
        _, stmts = node
        self.visit(stmts)

    def visit_for_stmt(self, node):
        var, iterable, stmts = node[1:]
        var_type, var_name = var
        var_type = self._get_ir_type(var_type)
        array = self.visit(iterable)
        array_alloc = self.builder.alloca(array.type)
        self.builder.store(array, array_alloc)
        loop_var = self.builder.alloca(var_type, name=var_name)
        loop_block = self.builder.append_basic_block(name="loop")
        after_loop_block = self.builder.append_basic_block(name="after_loop")
        self.builder.branch(loop_block)
        self.builder.position_at_start(loop_block)
        self.scope.enter()
        self.scope.define(var_name, loop_var)
        index_ptr = self.builder.alloca(ir.IntType(32), name="index")
        self.builder.store(ir.Constant(ir.IntType(32), 0), index_ptr)
        index = self.builder.load(index_ptr, "index")
        element_ptr = self.builder.gep(array_alloc, [ir.Constant(ir.IntType(32), 0), index])
        element = self.builder.load(element_ptr, "element")
        self.builder.store(element, loop_var)
        for stmt in stmts:
            self.visit(stmt)
        next_index = self.builder.add(index, ir.Constant(ir.IntType(32), 1), name="next_index")
        self.builder.store(next_index, index_ptr)
        end_cond = self.builder.icmp_signed("<", next_index, ir.Constant(ir.IntType(32), array.type.count))
        self.builder.cbranch(end_cond, loop_block, after_loop_block)
        self.builder.position_at_start(after_loop_block)
        self.scope.leave()

    def visit_switch_stmt(self, node):
        expr, cases = node[1:]
        expr_value = self.visit(expr)
        default_block = self.builder.append_basic_block(name="switch_default")
        self.switch_block = self.builder.switch(expr_value, default_block)
        self.scope.enter()
        for case in cases:
            self.visit(case)
        self.scope.leave()
        self.builder.position_at_end(default_block)

    def visit_case(self, node):
        value, stmts = node[1:]
        case_value = self.visit(value)
        case_block = self.builder.append_basic_block(name=f"case_{case_value.constant}")
        self.switch_block.add_case(case_value, case_block)
        self.builder.position_at_end(case_block)
        self.scope.enter()
        for stmt in stmts:
            self.visit(stmt)
        self.scope.leave()
        if not self.builder.block.is_terminated:
            self.builder.branch(self.switch_block)

    def visit_binop(self, node):
        op, lhs, rhs = node[1:]
        lhs = self.visit(lhs)
        rhs = self.visit(rhs)
        method = getattr(self.builder, self._get_op_method(op))
        if method:
            return method(lhs, rhs)
        else:
            raise Exception(f"Unknown binary operator {op}")

    def visit_comparison(self, node):
        op, lhs, rhs = node[1:]
        lhs = self.visit(lhs)
        rhs = self.visit(rhs)
        valid_ops = {'==', '!=', '<', '<=', '>', '>='}
        if op not in valid_ops:
            raise ValueError(f"Invalid comparison operator: {op}")
        return self.builder.icmp_signed(op, lhs, rhs)

    def visit_return(self, node):
        try:
            value = self.visit(node[1])
            self.builder.ret(value)
        except IndexError:
            self.builder.ret_void()

    def visit_identifier(self, node):
        var_name = node[1]
        try:
            var_alloca = self.scope.resolve(var_name)
            if var_alloca:
                return self.builder.load(var_alloca, var_name)
        except Exception:
            pass
        if self.current_instance:
            class_name = self.current_instance.type.pointee.name
            field_index = self._get_field_index(class_name, var_name)
            field_ptr = self.builder.gep(self.current_instance, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), field_index)])
            return self.builder.load(field_ptr, var_name)
        raise Exception(f"Undefined variable: {var_name}")

    def visit_range(self, node):
        start, end = node[1:]
        start_value = int(start[1])
        end_value = int(end[1])
        array = [(start[0], str(el)) for el in range(start_value, end_value)]
        return self.visit(('array_literal', array))

    def visit_integer(self, node):
        return ir.Constant(ir.IntType(32), int(node[1]))

    def visit_double(self, node):
        return ir.Constant(ir.DoubleType(), float(node[1]))

    def visit_string(self, node):
        return ir.Constant(ir.IntType(8).as_pointer(), node[1])

    def visit_boolean(self, node):
        value = 1 if node[1] == 'True' else 0
        return ir.Constant(ir.IntType(1), value)

    def visit_array_literal(self, node):
        elements = [self.visit(element) for element in node[1]]
        array_type = ir.ArrayType(elements[0].type, len(elements))
        return ir.Constant(array_type, elements)

    def visit_lambda(self, node):
        params, body = node[1:]
        param_types = [self._get_ir_type(param[0]) for param in params]
        func_type = ir.FunctionType(self._get_ir_type('int'), param_types)  # Assuming return type is int for simplicity
        func = ir.Function(self.module, func_type, name="lambda")
        
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        
        self.scope.enter()
        for idx, (param_type, param_name) in enumerate(params):
            ptr = self.builder.alloca(self._get_ir_type(param_type), param_name)
            self.builder.store(func.args[idx], ptr)
            self.scope.define(param_name, ptr)
        
        result = self.visit(body)
        self.builder.ret(result)
        self.scope.leave()
        # func.type = ir.FunctionType(result.type, param_types)
        
        return func

    def _generate_constructor(self, class_name, class_type, ctor_def):
        _, _, ctor_args, ctor_body = ctor_def
        param_types = [self._get_ir_type(param[0]) for param in ctor_args]
        func_type = ir.FunctionType(class_type.as_pointer(), param_types)
        ctor = ir.Function(self.module, func_type, name=f"{class_name}_ctor")
        entry_block = ctor.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)
        instance = self.builder.alloca(class_type)
        self.current_instance = instance
        for idx, (param_type, param_name) in enumerate(ctor_args):
            ptr = self.builder.alloca(self._get_ir_type(param_type), name=param_name)
            self.scope.define(param_name, ptr)
        for statement in ctor_body:
            self.visit(statement)
        if not self.builder.block.is_terminated:
            self.builder.ret(self.current_instance)
        self.current_instance = None

    def _generate_method(self, class_name, class_type, method_def):
        _, _, return_type, method_name, args, method_body = method_def
        llvm_return_type = self._get_ir_type(return_type)
        func_type = ir.FunctionType(llvm_return_type, [class_type.as_pointer()] + [self._get_ir_type(arg[0]) for arg in args])
        func = ir.Function(self.module, func_type, name=f"{class_name}_{method_name}")
        entry_block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)
        instance = self.builder.alloca(class_type)
        self.current_instance = instance
        self.scope.enter()
        for idx, (arg_type, arg_name) in enumerate(args):
            ptr = self.builder.alloca(self._get_ir_type(arg_type), name=arg_name)
            self.builder.store(func.args[idx + 1], ptr)
            self.scope.define(arg_name, ptr)
        for statement in method_body:
            self.visit(statement)
        self.scope.leave()
        if not self.builder.block.is_terminated:
            if isinstance(llvm_return_type, ir.VoidType):
                self.builder.ret_void()
            else:
                self.builder.ret(self._get_default_value(llvm_return_type))
        self.current_instance = None

    def _get_field_index(self, class_name, field_name):
        class_info = self.classes.get(class_name)
        if not class_info or field_name not in class_info["fields"]:
            raise ValueError(f"Field {field_name} not found in class {class_name}")
        return class_info["fields"][field_name]

    def _get_ir_type(self, type_name):
        match type_name:
            case 'int':
                return ir.IntType(32)
            case 'double':
                return ir.DoubleType()
            case 'bool':
                return ir.IntType(1)
            case 'str':
                return ir.IntType(8).as_pointer()
            case _:  # Handle user-defined types (e.g., classes)
                if type_name in self.classes:
                    return self.classes[type_name]["type"].as_pointer()
                raise Exception(f"Unsupported type: {type_name}")

    def _get_op_method(self, op):
        return {
            '+': 'add',
            '-': 'sub',
            '*': 'mul',
            '/': 'div',
            '%': 'urem',
            '**': 'fmul',
        }.get(op, None)

    def _get_default_value(self, ir_type):
        if isinstance(ir_type, ir.IntType):
            return ir.Constant(ir_type, 0)
        elif isinstance(ir_type, ir.DoubleType):
            return ir.Constant(ir_type, 0.0)
        elif isinstance(ir_type, ir.PointerType):
            return ir.Constant(ir_type, None)
        else:
            raise Exception(f"Unsupported type for default value: {ir_type}")
