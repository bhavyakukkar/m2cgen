from contextlib import contextmanager

from m2cgen.interpreters.code_generator import CodeTemplate, ImperativeCodeGenerator


class VyperCodeGenerator(ImperativeCodeGenerator):

    tpl_var_declaration = CodeTemplate("{var_name}: {type} = empty({type})")

    tpl_infix_expression = CodeTemplate("{left} {op} {right}")
    tpl_return_statement = CodeTemplate("return {value}")
    tpl_array_index_access = CodeTemplate("{array_name}[{index}]")
    tpl_if_statement = CodeTemplate("if {if_def}:")
    tpl_else_statement = CodeTemplate("else:")
    tpl_var_assignment = CodeTemplate("{var_name} = {value}")

    scalar_type = "decimal"
    dyn_vector_type = "DynArray[decimal, 2**8]"
    tpl_vector_type = CodeTemplate("decimal[{size}]")

    tpl_block_termination = CodeTemplate("")

    def add_var_declaration(self, size):
        var_name = self.get_var_name()
        self.add_code_line(self.tpl_var_declaration(
            var_name=var_name,
            type=self._get_var_declare_type(size)))
        return var_name

    def add_function_def(self, name, args, output_size):
        func_args = ", ".join([
            f"{n}: {self.dyn_vector_type if is_vector else self.scalar_type}"
            for is_vector, n in args])
        return_type = self._get_var_declare_type(output_size)
        function_def = f"@external\n@view\ndef {name}({func_args}) -> {return_type}:"
        self.add_code_line(function_def)
        self.increase_indent()

    @contextmanager
    def function_definition(self, name, args, output_size):
        self.add_function_def(name, args, output_size)
        yield

    def vector_init(self, values):
        return f"[{', '.join(values)}]"

    def add_dependency(self, dep):
        self.prepend_code_line(f"import {dep}")

    def _get_var_declare_type(self, size):
        if size > 1:
            return self.tpl_vector_type(size=size)
        else:
            return self.scalar_type

    def tpl_num_value(self, value):
        # Replace decimal numbers `x.y` where y exceeds 10 digits into `(x. + (y. / 100..))`
        # <https://docs.vyperlang.org/en/latest/types.html#id10>
        source = CodeTemplate("{value}")(value=value)
        whole, frac = source.split(".")
        if len(frac) <= 10:
            return source
        zeroes = "0" * len(frac)
        processed = f"({whole}. + ({frac.strip('0')}. / 1{zeroes}.))"
        return processed
