from collections import defaultdict
from skitso.movement import Movable, Point, Vector


class BaseImgElem(Movable):
    z_index = 0

    def draw_me(self, pencil, relative_to=None):
        raise NotImplementedError

    def add(self, child):
        raise NotImplementedError

    def __hash__(self):
        return hash(f"Skitso - {type(self).__name__} - {id(self)}")

    def __str__(self):
        return f"<{type(self).__name__} at {hex(id(self))}>"


class Container(BaseImgElem):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.children = []

    def add(self, item):
        if not isinstance(item, BaseImgElem):
            raise TypeError(f"Expected {BaseImgElem}, got {type(item)}")
        self.children.append(item)

    def remove(self, item):
        self.children.remove(item)

    @property
    def end(self):
        maxx, maxy = self.position
        for child in self.children:
            if child.end.x > maxx:
                maxx = child.end.x
            if child.end.y > maxy:
                maxy = child.end.y
        return Point(maxx, maxy)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        old_position = getattr(self, "_position", None)
        self._position = value
        if old_position is not None:
            delta = value - old_position
            for child in self.children:
                child.position += delta

    def iter_children(self, by_z_index=True):
        if not by_z_index:
            for child in self.children:
                yield child
        else:
            by_z = defaultdict(list)
            for child in self.children:
                z = getattr(child, 'z_index', 0)
                by_z[z].append(child)
            for z in sorted(by_z.keys()):
                for child in by_z[z]:
                    yield child

    def draw_me(self, pencil):
        # we are a container, so we need to draw all the children
        for child in self.iter_children():
            child.draw_me(pencil)
