from dataclasses import dataclass


@dataclass
class Geometry:
    x: float
    y: float
    width: float
    height: float

    def adjusted(
        self,
        left: float = 0,
        top: float = 0,
        right: float = 0,
        bottom: float = 0,
    ) -> "Geometry":

        return Geometry(
            x=self.x + left,
            y=self.y + top,
            width=self.width - left + right,
            height=self.height - top + bottom,
        )


@dataclass
class Color:
    r: int
    g: int
    b: int
    a: int = 255
