from dataclasses import dataclass
from enum import Enum


@dataclass
class Point:
    x: float
    y: float

    def __add__(self, other):
        if isinstance(other, Point):
            ox = other.x
            oy = other.y
        elif isinstance(other, Vector):
            ox = other.dx
            oy = other.dy
        elif isinstance(other, tuple) and len(other) == 2:
            ox, oy = other
        else:
            raise ValueError(f"Cannot add {type(other)} to Point")
        return Point(self.x + ox, self.y + oy)

    def __sub__(self, other):
        if not isinstance(other, Point):
            raise ValueError(f"Cannot substract {type(other)} to Point")
        return Vector(self.x - other.x, self.y - other.y)

    def __iter__(self):
        # allows easy conversion to tuple
        yield self.x
        yield self.y


@dataclass
class Vector:
    dx: float
    dy: float

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.dx + other.dx, self.dy + other.dy)
        else:
            raise ValueError(f"Cannot add {type(other)} to Vector")

    def __mul__(self, num):
        if not isinstance(num, (int, float)):
            raise ValueError(f"Cannot multiply Vector by {type(num)}")
        return Vector(self.dx * num, self.dy * num)

    def __iter__(self):
        # allows easy conversion to tuple
        yield self.dx
        yield self.dy


LEFT = Vector(-1, 0)
RIGHT = Vector(1, 0)
UP = Vector(0, -1)
DOWN = Vector(0, 1)


class AlignmentDial(Enum):
    LOW = -10
    HALF = 0
    HIGH = 10


class Aligment:
    def __init__(self, horizontal, vertical):
        self.horizontal = horizontal
        self.vertical = vertical

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Aligment) and self.horizontal == value.horizontal and self.vertical == value.vertical

    def __repr__(self):
        if self == TOP_EDGE:
            return "Aligment.TOP_EDGE"
        elif self == BOTTOM_EDGE:
            return "Aligment.BOTTOM_EDGE"
        elif self == CENTER_CENTER:
            return "Aligment.CENTER_CENTER"
        elif self == LEFT_EDGE:
            return "Aligment.LEFT_EDGE"
        elif self == RIGHT_EDGE:
            return "Aligment.RIGHT_EDGE"
        else:
            return f"Aligment(horizontal={self.horizontal}, vertical={self.vertical})"


TOP_EDGE = Aligment(None, AlignmentDial.LOW)
BOTTOM_EDGE = Aligment(None, AlignmentDial.HIGH)
CENTER_CENTER = Aligment(AlignmentDial.HALF, AlignmentDial.HALF)
LEFT_EDGE = Aligment(AlignmentDial.LOW, None)
RIGHT_EDGE = Aligment(AlignmentDial.HIGH, None)


class Movable:
    # Every Movable must have a position that represents:
    # - it's current location (starts at 0, 0 which is the top-left corner of the screen)
    #
    # Also, it has an "end" property that returns the lowest-right corner of the Movable,
    # such property MUST be dynamically computed based on the Movable's position, so if position
    # changes, the "end" value changes as well.
    #
    # Together, position and end makes possible the "align_to" method.

    def __init__(self, position, *args, **kwargs) -> None:
        if not isinstance(position, Point):
            raise ValueError(f"Expected Point, got {type(position)}")
        self.position = position

    @property
    def end(self):
        raise NotImplementedError('Not implemented "end" for %s' % self.__class__.__name__)

    @property
    def box_height(self):
        return self.end.y - self.position.y

    @property
    def box_width(self):
        return self.end.x - self.position.x

    def move_to(self, point):
        if not isinstance(point, Point):
            raise ValueError(f"Expected Point, got {type(point)}")
        self.position = point

    def shift(self, vector):
        if not isinstance(vector, Vector):
            raise ValueError(f"Expected Vector, got {type(vector)}")
        self.position += vector

    def move_end_to(self, point):
        if not isinstance(point, Point):
            raise ValueError(f"Expected Point, got {type(point)}")
        # Given that "end" it's a property, we need to move the position in such a way that
        # the end of the Movable is at the requested point
        current_end = self.end
        delta = point - current_end
        self.position += delta
        assert self.end == point

    def to_edge(self, other, alignment):
        # Makes coincide the edge of "self" with requested edges of "other"
        if not isinstance(other, Movable):
            raise ValueError(f"Expected Movable, got {type(other)}")
        if not isinstance(alignment, Aligment):
            raise ValueError(f"Expected Aligment, got {type(alignment)}")

        current_end = self.end
        if alignment.vertical is None:
            new_y = self.position.y  # leave y unchanged
        elif alignment.vertical == AlignmentDial.LOW:  # top edge
            new_y = other.position.y
        elif alignment.vertical == AlignmentDial.HIGH:  # bottom edge
            new_y = other.end.y - (current_end.y - self.position.y)
        else:  # vertical center
            other_delta_y = other.end.y - other.position.y
            self_delta_y = current_end.y - self.position.y
            new_y = other.position.y + (other_delta_y - self_delta_y) / 2

        if alignment.horizontal is None:
            new_x = self.position.x  # leave x unchanged
        elif alignment.horizontal == AlignmentDial.LOW:  # left edge
            new_x = other.position.x
        elif alignment.horizontal == AlignmentDial.HIGH:  # right edge
            new_x = other.end.x - (current_end.x - self.position.x)
        else:  # horizontal center
            other_delta_x = other.end.x - other.position.x
            self_delta_x = current_end.x - self.position.x
            new_x = other.position.x + (other_delta_x - self_delta_x) / 2

        self.move_to(Point(new_x, new_y))

    def center_respect_to(self, other):
        self.to_edge(other, CENTER_CENTER)
