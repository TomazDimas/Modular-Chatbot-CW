
from __future__ import annotations
import ast
import operator as op

OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
}
UNARY = {
    ast.UAdd: lambda x: x,
    ast.USub: lambda x: -x,
}

class MathError(ValueError):
    pass

def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))

    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY:
        return UNARY[type(node.op)](_eval(node.operand))

    raise MathError("Expressão não suportada")

def eval_expr(expr: str) -> float:
    try:
        node = ast.parse(expr, mode="eval").body
        val = float(_eval(node))
        if val in (float("inf"), float("-inf")):
            raise MathError("Resultado infinito")
        return round(val, 2)
    except ZeroDivisionError:
        raise MathError("Divisão por zero")
    except MathError:
        raise
    except Exception:
        raise MathError("Expressão inválida")
