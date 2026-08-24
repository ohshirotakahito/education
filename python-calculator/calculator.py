import ast
import math
import operator


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression: str, angle_mode: str = "DEG") -> float | int:
    """Safely calculate an arithmetic expression."""
    expression = expression.strip().replace("×", "*").replace("÷", "/").replace("^", "**")
    if not expression:
        raise ValueError("式を入力してください")
    if len(expression) > 200:
        raise ValueError("式が長すぎます")
    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body, angle_mode)
    except ZeroDivisionError as error:
        raise ValueError("0では割れません") from error
    except (SyntaxError, TypeError, ValueError, OverflowError) as error:
        if isinstance(error, ValueError) and str(error) in {"式を入力してください", "式が長すぎます", "0では割れません"}:
            raise
        raise ValueError("計算式を確認してください") from error
    if isinstance(result, complex) or abs(result) > 1e100:
        raise ValueError("計算結果が大きすぎます")
    return int(result) if isinstance(result, float) and result.is_integer() else result


def _evaluate(node, angle_mode="DEG"):
    if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = _evaluate(node.left, angle_mode)
        right = _evaluate(node.right, angle_mode)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("指数が大きすぎます")
        return OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_evaluate(node.operand, angle_mode))
    if isinstance(node, ast.Name) and node.id in {"pi", "e"}:
        return math.pi if node.id == "pi" else math.e
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and len(node.args) == 1 and not node.keywords:
        value = _evaluate(node.args[0], angle_mode)
        name = node.func.id
        if name in {"sin", "cos", "tan"}:
            angle = math.radians(value) if angle_mode == "DEG" else value
            return {"sin": math.sin, "cos": math.cos, "tan": math.tan}[name](angle)
        functions = {"sqrt": math.sqrt, "log": math.log10, "ln": math.log}
        if name in functions:
            return functions[name](value)
        if name == "fact" and isinstance(value, int) and 0 <= value <= 100:
            return math.factorial(value)
    raise ValueError("使用できない式です")


def format_number(value) -> str:
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)
