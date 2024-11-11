from pathlib import Path
from PIL import Image, ImageDraw

from skitso.atom import Container


class Scene(Container):

    def __init__(self, canvas_size, base_folder_path, color="black"):
        self.color = color
        self.width, self.height = canvas_size
        self.create_canvas()
        self.folder_path = (
            Path(base_folder_path) / type(self).__name__.lower() / "frames"
        )
        self.folder_path.mkdir(parents=True, exist_ok=True)
        self.next_tick_id = 1
        self.children = []

    def create_canvas(self):
        self.image = Image.new("RGB", (self.width, self.height), self.color)
        self.draw = ImageDraw.Draw(self.image)
        self.draw.image = self.image
        self.draw.fontmode = "L"

    def tick(self):
        # need to create the image from scratch
        self.create_canvas()
        for item in self.children:
            item.draw_me(self.draw)

        new_img_path = self.folder_path / f"{self.next_tick_id:08}.jpg"
        im = self.image.resize(
            (self.width * 2, self.height * 2), resample=Image.Resampling.LANCZOS
        )
        im = im.resize((self.width, self.height), resample=Image.Resampling.LANCZOS)
        im.save(new_img_path, subsampling=0, quality=95)
        self.next_tick_id += 1

    def add(self, item):
        self.children.append(item)
