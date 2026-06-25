from dataclasses import dataclass


@dataclass
class Geometry:
    x: float
    y: float
    width: float
    height: float


@dataclass
class Color:
    r: int
    g: int
    b: int
    a: int = 255
