from dataclasses import dataclass
from typing import List, Optional

LOGICALS = ["And", "Or", "Not"]
COMPARISONS = ["<", ">", "==", "<=", ">=", "!="]


@dataclass
class Expression:
    pass


@dataclass
class LogicalExpression(Expression):
    op: str
    args: list[Expression]


@dataclass
class ComparisonExpression(Expression):
    left: str
    op: str
    right: str


@dataclass
class IfExpression(Expression):
    condition: Expression
    thenBlock: List[Expression]
    elseBlock: Optional[List[Expression]] = None
