from pathlib import Path

from m2cgen.ast import BinNumOpType
from m2cgen.interpreters.code_generator import CodeTemplate
from m2cgen.interpreters.interpreter import ImperativeToCodeInterpreter
from m2cgen.interpreters.mixins import BinExpressionDepthTrackingMixin, LinearAlgebraMixin, PowExprFunctionMixin
from m2cgen.interpreters.utils import get_file_content
from m2cgen.interpreters.vyper.code_generator import VyperCodeGenerator


class VyperInterpreter(ImperativeToCodeInterpreter,
                       PowExprFunctionMixin,
                       BinExpressionDepthTrackingMixin,
                       LinearAlgebraMixin):

    # 60 raises MemoryError for some SVM models with RBF kernel.
    bin_depth_threshold = 55

    supported_bin_vector_ops = {
        BinNumOpType.ADD: lambda size: f"self.add_vectors_{size}",
    }

    supported_bin_vector_num_ops = {
        BinNumOpType.MUL: lambda size: f"self.mul_vector_number_{size}",
    }

    power_function_name = NotImplemented

    with_sigmoid_expr = False
    with_softmax_expr = False

    # set of sizes needed of the `add_vectors`
    add_vector_sizes = {}
    # set of sizes needed of the `mul_vector_number`
    mul_vector_number_sizes = {}

    def __init__(self, indent=4, function_name="score", *args, **kwargs):
        self.function_name = function_name

        cg = VyperCodeGenerator(indent=indent)
        super().__init__(cg, *args, **kwargs)

    # override
    def interpret_bin_vector_expr(self, expr, extra_func_args=(), **kwargs):
        if expr.op not in self.supported_bin_vector_ops:
            raise NotImplementedError(f"Op '{expr.op.name}' is unsupported")

        # self.with_linear_algebra = True
        size = expr.left.output_size
        self.add_vector_sizes[size] = True
        function_name = self.supported_bin_vector_ops[expr.op](size)

        return self._cg.function_invocation(
            function_name,
            self._do_interpret(expr.left, **kwargs),
            self._do_interpret(expr.right, **kwargs),
            *extra_func_args)

    # override
    def interpret_bin_vector_num_expr(self, expr, extra_func_args=(), **kwargs):
        if expr.op not in self.supported_bin_vector_num_ops:
            raise NotImplementedError(f"Op '{expr.op.name}' is unsupported")

        size = expr.left.output_size
        self.mul_vector_number_sizes[size] = True
        function_name = self.supported_bin_vector_num_ops[expr.op](size)

        return self._cg.function_invocation(
            function_name,
            self._do_interpret(expr.left, **kwargs),
            self._do_interpret(expr.right, **kwargs),
            *extra_func_args)

    def interpret(self, expr):
        self._cg.reset_state()
        self._reset_reused_expr_cache()

        with self._cg.function_definition(
                name=self.function_name,
                args=[(True, self._feature_array_name)],
                output_size=expr.output_size):
            last_result = self._do_interpret(expr)
            self._cg.add_return_statement(last_result)

        current_dir = Path(__file__).absolute().parent

        # linear-algebra
        if bool(self.add_vector_sizes):
            filename = current_dir / "add_vectors.vy"
            for size in self.add_vector_sizes:
                self._cg.prepend_code_lines(CodeTemplate(get_file_content(filename))(size=size))
        if bool(self.mul_vector_number_sizes):
            filename = current_dir / "mul_vector_number.vy"
            for size in self.mul_vector_number_sizes:
                self._cg.prepend_code_lines(CodeTemplate(get_file_content(filename))(size=size))

        if self.with_softmax_expr:
            raise NotImplementedError
            filename = current_dir / "softmax.vy"
            self._cg.prepend_code_lines(get_file_content(filename))

        if self.with_sigmoid_expr:
            raise NotImplementedError
            filename = current_dir / "sigmoid.vy"
            self._cg.prepend_code_lines(get_file_content(filename))

        if self.with_math_module:
            raise NotImplementedError
            self._cg.add_dependency("math")

        return self._cg.finalize_and_get_generated_code()

    def interpret_abs_expr(self, expr, **kwargs):
        nested_result = self._do_interpret(expr.expr, **kwargs)
        return self._cg.function_invocation(
            self.abs_function_name, nested_result)

    def interpret_softmax_expr(self, expr, **kwargs):
        self.with_softmax_expr = True
        return super().interpret_softmax_expr(expr, **kwargs)

    def interpret_sigmoid_expr(self, expr, **kwargs):
        self.with_sigmoid_expr = True
        return super().interpret_sigmoid_expr(expr, **kwargs)
