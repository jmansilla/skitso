import math
from PIL import Image, ImageFont, ImageDraw

from skitso.atom import BaseImgElem, Container, Point


class Rectangle(BaseImgElem):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        fill_color,
        fill_opacity=None,
        stroke_color=None,
        stroke_width=None,
    ):
        super().__init__(Point(x, y))
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width

    @property  # needed for movable API
    def end(self):
        return Point(self.x + self.width, self.y + self.height)

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def x1y1x2y2(self):
        pfrom, pto = self.position, self.end
        return pfrom.x, pfrom.y, pto.x, pto.y

    def _draw_kw(self):
        kw = {}
        kw["fill"] = self.fill_color
        if self.stroke_width is not None and self.stroke_color is not None:
            kw["width"] = self.stroke_width
            kw["outline"] = self.stroke_color
        return kw

    def draw_me(self, pencil):
        kw = self._draw_kw()
        pencil.rectangle(self.x1y1x2y2(), **kw)


class RoundedRectangle(Rectangle):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        fill_color,
        fill_opacity=None,
        stroke_color=None,
        stroke_width=None,
        corner_radius=None,
    ):
        super().__init__(
            x, y, width, height, fill_color, fill_opacity, stroke_color, stroke_width
        )
        self.corner_radius = corner_radius

    def _draw_kw(self):
        kw = super()._draw_kw()
        kw["radius"] = self.corner_radius
        return kw

    def draw_me(self, pencil):
        kw = self._draw_kw()
        pencil.rounded_rectangle(self.x1y1x2y2(), **kw)


class Line(BaseImgElem):
    def __init__(self, x1, y1, x2, y2, color, thickness):
        # Lets compute the inserion point: the top-leftmost point of (not the line)
        # but of the wrapping rectangle around the line
        position = Point(min(x1, x2), min(y1, y2))
        super().__init__(position)
        self.relative_end = Point(max(x1, x2), max(y1, y2)) - position
        self.line_from = Point(x1 - position.x, y1 - position.y)
        self.line_to = Point(x2 - position.x, y2 - position.y)
        self.color = color
        self.thickness = thickness

    @property
    def end(self):
        return self.position + self.relative_end

    def draw_me(self, pencil):
        shift = self.position
        x1, y1 = shift + self.line_from
        x2, y2 = shift + self.line_to
        pencil.line((x1, y1, x2, y2), fill=self.color, width=self.thickness)

    def get_slope(self, in_degrees=False):
        # 0 is the horizontal axis to the right. Pi (or 180°) its the opposite
        # Pi/2 it's the vertical going up, and 3/2 * Pi going down.
        delta = self.line_from - self.line_to
        slope = math.atan2(delta.dy, delta.dx)
        if in_degrees:
            slope = slope * 180 / math.pi
        return slope

    def get_length(self):
        delta = self.line_from - self.line_to
        return (delta.dx**2 + delta.dy**2) ** (1 / 2)


class ArrowTip(BaseImgElem):
    def __init__(self, x, y, height, angle, color):
        # Arrow tip should be poiting exactly at x,y and the direction
        # should be the same as the vector
        # Arrow tip height is measured over such direction
        self.color = color
        self.height = height
        self.base = height  # can be changed later
        self.tip_angle = angle

        vertices = self.compute_vertices(x, y)
        min_x = min(v.x for v in vertices)
        min_y = min(v.y for v in vertices)
        super().__init__(Point(min_x, min_y))
        self.relative_vertices = [Point(v.x - min_x, v.y - min_y) for v in vertices]
        self.relative_end = Point(
            max(v.x for v in vertices) - min_x, max(v.y for v in vertices) - min_y
        )

    @property
    def end(self):
        return self.position + self.relative_end

    def draw_me(self, pencil):
        shift = self.position
        positioned_triangle = [vtx + shift for vtx in self.relative_vertices]
        raw = [(vtx.x, vtx.y) for vtx in positioned_triangle]
        pencil.polygon(raw, fill=self.color)

    def compute_vertices(self, tip_x, tip_y):
        half_base = self.base / 2
        alpha = math.atan(half_base / self.height) * 180 / math.pi
        hypothenuse = (self.height**2 + half_base**2) ** (1 / 2)
        v0 = Point(tip_x, tip_y)
        vertices = [v0]
        for beta in [self.tip_angle - alpha, self.tip_angle + alpha]:
            beta_radians = beta * math.pi / 180
            vertex_x = math.cos(beta_radians) * hypothenuse
            vertex_y = math.sin(beta_radians) * hypothenuse
            vertices.append(v0 + Point(vertex_x, vertex_y))
        return vertices


class Arrow(BaseImgElem):
    def __init__(self, x1, y1, x2, y2, color, thickness, tip_height):
        self.line = Line(x1, y1, x2, y2, color, thickness)
        # ArrowTip is at (x2, y2)
        # Arrow tip height is measured over the direction of the line
        angle = self.line.get_slope(in_degrees=True)
        self.tip = ArrowTip(x2, y2, tip_height, angle, color)
        self.tip_delta = self.tip.position - self.position

        # Line is drawn from (x1, y1) to (x2, y2). But if thickness != 1
        # line will be shortened a bit to not provoke a weird broken pointy arrow
        if thickness > 1:
            # we will truncate half tip_height.
            chopped_length = tip_height / 2
            angle_radians = angle * math.pi / 180
            chopped_x = math.cos(angle_radians) * chopped_length
            chopped_y = math.sin(angle_radians) * chopped_length
            self.truncated_line = Line(
                x1, y1, x2 + chopped_x, y2 + chopped_y, color, thickness
            )
        else:
            self.truncated_line = None

    @property
    def position(self):
        return self.line.position

    @position.setter
    def position(self, value):
        self.line.position = value
        self.tip.position = value + self.tip_delta
        if self.truncated_line is not None:
            self.truncated_line.position = value

    @property
    def end(self):
        return self.line.end

    @property
    def color(self):
        return self.line.color

    @property
    def thickness(self):
        return self.line.thickness

    def draw_me(self, pencil):
        self.tip.draw_me(pencil)
        if self.truncated_line is not None:
            self.truncated_line.draw_me(pencil)
        else:
            self.line.draw_me(pencil)


class Text(BaseImgElem):
    def __init__(
        self, x, y, text, font_name, font_size, color="white", align="left"
    ):
        super().__init__(Point(x, y))
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.color = color
        self.align = align
        self.font = self.load_font()

    def load_font(self):
        return ImageFont.load_default(self.font_size)

    @property
    def end(self):
        if not hasattr(self, "relative_end"):
            temp_img = Image.new("RGBA", (1000, 1000))
            temp_draw = ImageDraw.Draw(temp_img)
            box = temp_draw.textbbox((0, 0), self.text, font=self.font)
            self.relative_end = Point(box[2], box[3])
        return self.position + self.relative_end

    def get_params(self):
        return {"stroke_fill": None, "stroke_width": 0, "fill": self.color, "align": self.align}

    def draw_me(self, pencil):
        font = self.load_font()
        x, y = self.position
        pencil.text((x, y), self.text, font=font, **self.get_params())
