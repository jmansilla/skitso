from pathlib import Path
from PIL import Image, ImageDraw

from skitso.atom import Container, Point


class Scene(Container):

    def __init__(self, canvas_size, base_folder_path, color="black", antialias=False,
                 file_extension="jpg"):
        super().__init__(position=Point(0, 0))
        self.color = color
        self.width, self.height = canvas_size
        self.create_canvas()
        self.build_folder(base_folder_path)
        self.next_tick_id = 1
        self.antialias = antialias
        self.file_extension = file_extension

    def build_folder(self, base_folder_path):
        self.folder_path = (
            Path(base_folder_path) / type(self).__name__.lower() / "frames"
        )
        self.folder_path.mkdir(parents=True, exist_ok=True)

    def create_canvas(self):
        self.image = Image.new("RGB", (self.width, self.height), self.color)
        self.draw = ImageDraw.Draw(self.image)
        self.draw.image = self.image  # type: ignore
        self.draw.fontmode = "L"

    def tick(self):
        # need to create the image from scratch
        self.create_canvas()
        for item in self.iter_children():
            item.draw_me(self.draw)
        ext = self.file_extension
        new_img_path = self.folder_path / f"{self.next_tick_id:08}.{ext}"
        if self.antialias:
            # only known way to get antialiasing: resize up and down.
            im = self.image.resize(
                (self.width * 2, self.height * 2), resample=Image.Resampling.LANCZOS
            )
            im = im.resize((self.width, self.height), resample=Image.Resampling.LANCZOS)
        else:
            im = self.image
        im.save(new_img_path, subsampling=0, quality=95)
        self.next_tick_id += 1
