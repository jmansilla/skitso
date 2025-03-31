# SKITSO

    greek for drafting


## What it's skitso?

Built on top of [Pillow](https://pypi.org/project/pillow/), skitso it's a lightweight scenes generator. It may be think as newborn nephew of [manim](https://docs.manim.community/en/stable/index.html).

        It's way smaller, and it's somehow related.

With very simple shape primitives you can define your scene, and them you explicitely take snapshots of the frames you want to capture.
That's it.


## A bit more of details:

 - You create simple geometric visual elements (Lines, Rectangles, Arrows). Their basic characteristics (dimensions, size, color, and positioning on a Cartesian plane) are used to generate a specific graphical representation using the @pillow library
 - You can define new objets, based on simpler ones as composition of them.
 - Each object (simple, complex, or user defined) can be precicely placed on the space.
 - Scene module, which is basically  a collection of visual objects, and a method `tick` which exports the current composition to a sequentially numerated frame (png file).

## Examples

### Simplest scene

```python
from skitso.scene import Scene
from skitso.shapes import Rectangle, Line

class SimplestScene(Scene):

   def render(self):
       self.tick()
       self.add(Rectangle(x=100, y=100, width=100, height=100, fill_color="red"))
       self.tick()
       self.add(Line(0, 0, 600, 400, "white", 1))
       self.tick()

if __name__ == "__main__":
   canvas_size = (600, 600)
   my_scene = SimplestScene(canvas_size, "output_path", "black")
   my_scene.render()
```

That will create the 3 following frames

<div>
<img style="float:left" src="https://github.com/jmansilla/skitso/blob/main/images/01.jpg?raw=true" alt="Frame 01" width="250"/>
<img style="float:left" src="https://github.com/jmansilla/skitso/blob/main/images/02.jpg?raw=true" alt="Frame 02" width="250"/>
<img style="float:left" src="https://github.com/jmansilla/skitso/blob/main/images/03.jpg?raw=true" alt="Frame 03" width="250"/>
</div>


### Creating new object kind, and displacements

And instead, if you want to get a feeling of creating new objects lets work with `namedrectangles`

```python
from skitso.atom import Container, Point
from skitso.shapes import Rectangle, Text

class NamedRectangle(Container):
   def __init__(self, x, y, width, height, fill_color, name):
       super().__init__(Point(x, y))
       self.name = name
       self.add(Rectangle(x, y, width, height, fill_color=fill_color))
       self.add(Text(x * 1.05, y, self.name, font_name="Monospace",
                     font_size=28, color="white", stroke_fill="gray", stroke_width=1))
```

And now a scene where this new figure is used, and where objects are moved between frames

```python
class MazeScene(Scene):
   def render(self):
       canvas_height, canvas_width = self.height, self.width
       offset = canvas_height / 15
       rectangles = []
       # Create concentric colored NamedRectangles
       colors = ["tomato", "firebrick", "maroon", "rebeccapurple", "midnightblue",]
       for i, color in enumerate(colors, start=1):
           margin = offset * 2 * i
           new_rect = NamedRectangle(
               x=offset * i, y=offset * i, fill_color=color, name=color,
               width=canvas_width - margin, height=canvas_height - margin,
           )
           rectangles.append(new_rect)
           self.add(new_rect)
       # Initial frame with all rectangles
       self.tick()

       # Move all rectangles to the right
       gravity_corner = mov.Aligment(mov.AlignmentDial.LOW, mov.AlignmentDial.HIGH)
       for i in range(len(rectangles) - 1):
           rect = rectangles[i + 1]
           prev = rectangles[i]
           rect.to_edge(prev, gravity_corner)
           self.tick()
```

The frames generated in this case are the ones that follow. Take a look of how each named-rectangle falls down between each frame.
<div>
<img style="float:left" src="https://github.com/jmansilla/skitso/blob/main/images/04.jpg?raw=true" alt="Frame 04" width="250"/>
<img style="float:left" src="https://github.com/jmansilla/skitso/blob/main/images/05.jpg?raw=true" alt="Frame 05" width="250"/>
<img style="float:left" src="https://github.com/jmansilla/skitso/blob/main/images/06.jpg?raw=true" alt="Frame 06" width="250"/>
<img style="float:left" src="https://github.com/jmansilla/skitso/blob/main/images/07.jpg?raw=true" alt="Frame 07" width="250"/>
<img style="float:left" src="https://github.com/jmansilla/skitso/blob/main/images/08.jpg?raw=true" alt="Frame 08" width="250"/>
</div>
