from PIL import Image, ImageOps
from rich.text import Text
import io
import urllib.request #downloads images

def image_to_color_blocks(image_source, width=120):
    image = Image.open(image_source).convert("RGB")
    aspect_ratio = image.height / image.width
    height = int(width * aspect_ratio * 0.5)
    image = image.resize((width, height), Image.Resampling.LANCZOS)

    pixels = image.getdata()
    output = Text()
    for i, (r, g, b) in enumerate(pixels):
        output.append(" ", style=f"on rgb({r},{g},{b})")
        if (i + 1) % width == 0:
            output.append("\n")
    return output

def get_thumbnail_art(source, width=60):
    if not source:
        return None
    try:
        if source.startswith("http://") or source.startswith("https://"):
            with urllib.request.urlopen(source) as response:
                image_bytes = io.BytesIO(response.read())
            return image_to_color_blocks(image_bytes, width=width)
        return image_to_color_blocks(source, width=width)
    except Exception:
        return None
