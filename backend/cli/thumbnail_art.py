from PIL import Image, ImageOps
import urllib.request #downloads images

def image_to_color_blocks(image_path, width=120):
    image = Image.open(image_path).convert("RGB")  #converting image to rgb valyes
    aspect_ratio = image.height / image.width
    height = int(width * aspect_ratio * 0.5)
    image = image.resize((width, height), Image.Resampling.LANCZOS)

    pixels = image.getdata()
    output = ""
    for i, (r, g, b) in enumerate(pixels):
        output += f"\033[48;2;{r};{g};{b}m "
        if (i + 1) % width == 0:
            output += "\033[0m\n"
    return output
