from dataclasses import dataclass
from typing import Any, Iterable, List, Tuple

from typing_extensions import Protocol


def central_difference(f: Any, *vals: Any, arg: int = 0, epsilon: float = 1e-6) -> Any:
    r"""
    Computes an approximation to the derivative of `f` with respect to one arg.

    See :doc:`derivative` or https://en.wikipedia.org/wiki/Finite_difference for more details.

    Args:
        f : arbitrary function from n-scalar args to one value
        *vals : n-float values $x_0 \ldots x_{n-1}$
        arg : the number $i$ of the arg to compute the derivative
        epsilon : a small constant

    Returns:
        An approximation of $f'_i(x_0, \ldots, x_{n-1})$
    """
    vals1 = [v for v in vals]
    vals2 = [v for v in vals]
    vals1[arg] = vals1[arg] + epsilon
    vals2[arg] = vals2[arg] - epsilon
    delta = f(*vals1) - f(*vals2)
    return delta / (2 * epsilon)


variable_count = 1


class Variable(Protocol):
    def accumulate_derivative(self, x: Any) -> None:
        pass

    @property
    def unique_id(self) -> int:
        pass

    def is_leaf(self) -> bool:
        pass

    def is_constant(self) -> bool:
        pass

    @property
    def parents(self) -> Iterable["Variable"]:
        pass

    def chain_rule(self, d_output: Any) -> Iterable[Tuple["Variable", Any]]:
        pass


def topological_sort(variable: Variable) -> Iterable[Variable]:
    """
    Computes the topological order of the computation graph.

    Args:
        variable: The right-most variable

    Returns:
        Non-constant Variables in topological order starting from the right.
    """
    # BEGIN ASSIGN1_1
    # TODO
    permanent_marked = []
    temporary_marked = []
    result = []

    def visit(n):
        if n.is_constant():
            return
        if n.unique_id in permanent_marked:
            return
        elif n.unique_id in temporary_marked:
            raise(RuntimeError("Not a DAG"))
        temporary_marked.append(n.unique_id)
        if n.is_leaf():
            pass
        else:
            for input in n.history.inputs:
                visit(input)
        
        temporary_marked.remove(n.unique_id)
        permanent_marked.append(n.unique_id)

        result.insert(0, n)


    visit(variable)
    return result

    # raise NotImplementedError("Task Autodiff Not Implemented Yet")
    # return stack
    # END ASSIGN1_1


def backpropagate(variable: Variable, deriv: Any) -> None:
    """
    Runs backpropagation on the computation graph in order to
    compute derivatives for the leave nodes.

    Args:
        variable: The right-most variable
        deriv  : Its derivative that we want to propagate backward to the leaves.

    No return. Should write to its results to the derivative values of each leaf through `accumulate_derivative`.
    """
    # BEGIN ASSIGN1_1
    # TODO
    order = topological_sort(variable)
    derivs = {variable.unique_id: deriv}
    for node in order:
        d_output = derivs[node.unique_id]
        if node.is_leaf():
            node.accumulate_derivative(d_output)
        else:
            # for input, d in node.history.backprop_step(d_output):
            # backprop_step = node.history.last_fn.chain_rule(node.history.ctx, node.history.inputs, d_output)

            for input, d in node.chain_rule(d_output):
                if input.unique_id not in derivs:
                    derivs[input.unique_id] = 0.0
                derivs[input.unique_id] += d
    return
    # END ASSIGN1_1


@dataclass
class Context:
    """
    Context class is used by `Function` to store information during the forward pass.
    """

    no_grad: bool = False
    saved_values: Tuple[Any, ...] = ()

    def save_for_backward(self, *values: Any) -> None:
        "Store the given `values` if they need to be used during backpropagation."
        if self.no_grad:
            return
        self.saved_values = values

    @property
    def saved_tensors(self) -> Tuple[Any, ...]:
        return self.saved_values
