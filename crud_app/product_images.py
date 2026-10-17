import io

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = 400, 300


def _hex_to_rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def _font(size):
    for path in (
        r'C:\Windows\Fonts\segoeuib.ttf',
        r'C:\Windows\Fonts\arialbd.ttf',
        r'C:\Windows\Fonts\calibrib.ttf',
        r'C:\Windows\Fonts\arial.ttf',
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _background(color):
    top = _lerp(color, (255, 255, 255), 0.82)
    bottom = _lerp(color, (255, 255, 255), 0.55)
    image = Image.new('RGB', (WIDTH, HEIGHT))
    pixels = image.load()
    for y in range(HEIGHT):
        row = _lerp(top, bottom, y / HEIGHT)
        for x in range(WIDTH):
            pixels[x, y] = row
    return image


def _floor_shadow(canvas, half_width, y, half_height=28):
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(
        [CENTER_X - half_width, y - half_height, CENTER_X + half_width, y + half_height],
        fill=(15, 23, 42, 60),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(14))
    canvas.alpha_composite(layer)


def _draw_name(canvas, name):
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = _font(30)
    width = draw.textlength(name, font=font)
    draw.text((CENTER_X - width / 2 + 2, 508 + 2), name, font=font, fill=(15, 23, 42, 110))
    draw.text((CENTER_X - width / 2, 508), name, font=font, fill=(15, 23, 42, 255))
    canvas.alpha_composite(layer)


def _draw_watermark(draw):
    font = _font(16)
    draw.text((WIDTH - 16, HEIGHT - 14), 'TechShop', font=font, fill=(15, 23, 42, 70), anchor='rd')


def _smartphone(draw, color):
    cx = CENTER_X
    dark = _lerp(color, (0, 0, 0), 0.55)
    draw.rounded_rectangle((cx - 92, 130, cx + 92, 455), radius=40, fill=dark)
    draw.rounded_rectangle((cx - 82, 145, cx + 82, 440), radius=30, fill=_lerp(color, (255, 255, 255), 0.18))
    draw.ellipse((cx - 7, 155, cx + 7, 169), fill=(15, 23, 42, 220))
    for i, accent in enumerate(('#ffffff', '#fbbf24', '#34d399')):
        x = cx - 30 + i * 30
        draw.rounded_rectangle((x - 11, 200, x + 11, 222), radius=6, fill=accent)
    draw.rounded_rectangle((cx - 38, 425, cx + 38, 431), radius=3, fill=(255, 255, 255, 150))


def _headphone(draw, color):
    cx = CENTER_X
    dark = _lerp(color, (0, 0, 0), 0.3)
    draw.arc((cx - 145, 120, cx + 145, 280), start=180, end=360, fill=color, width=26)
    for dx in (-145, 145):
        cup = (cx + dx - 58, 210, cx + dx + 58, 330)
        draw.rounded_rectangle(cup, radius=26, fill=dark)
        draw.rounded_rectangle(
            (cup[0] + 8, cup[1] + 8, cup[2] - 8, cup[3] - 8), radius=18, fill=_lerp(color, (0, 0, 0), 0.05)
        )
        draw.rounded_rectangle(
            (cup[0] + 12, cup[1] + 12, cup[2] - 12, cup[1] + 42), radius=12, fill=(255, 255, 255, 60)
        )


def _backpack(draw, color):
    cx = CENTER_X
    dark = _lerp(color, (0, 0, 0), 0.35)
    light = _lerp(color, (255, 255, 255), 0.25)
    draw.rounded_rectangle((cx - 115, 185, cx + 115, 385), radius=52, fill=color)
    draw.rounded_rectangle((cx + 45, 185, cx + 115, 385), radius=30, fill=dark)
    draw.arc((cx - 34, 150, cx + 34, 225), start=180, end=360, fill=dark, width=16)
    draw.rounded_rectangle((cx - 78, 250, cx + 78, 385), radius=24, fill=light)
    draw.line((cx, 268, cx, 372), fill=dark, width=4)
    draw.rounded_rectangle((cx - 16, 252, cx + 16, 268), radius=6, fill=(255, 255, 255, 200))
    for dx in (-108, 108):
        draw.rounded_rectangle((cx + dx - 8, 200, cx + dx + 8, 240), radius=4, fill=dark)


def _watch(draw, color):
    cx = CENTER_X
    dark = _lerp(color, (0, 0, 0), 0.4)
    draw.rounded_rectangle((cx - 42, 120, cx + 42, 210), radius=16, fill=dark)
    draw.rounded_rectangle((cx - 42, 375, cx + 42, 465), radius=16, fill=dark)
    draw.rounded_rectangle((cx - 92, 190, cx + 92, 395), radius=40, fill=_lerp(color, (0, 0, 0), 0.15))
    draw.rounded_rectangle((cx - 74, 208, cx + 74, 377), radius=24, fill=_lerp(color, (255, 255, 255), 0.15))
    draw.line((cx, 292, cx, 240), fill=(255, 255, 255, 255), width=9)
    draw.line((cx, 292, cx + 34, 315), fill=(255, 255, 255, 255), width=9)
    draw.ellipse((cx - 8, 284, cx + 8, 300), fill=(255, 255, 255, 255))
    draw.rounded_rectangle((cx + 92, 262, cx + 110, 322), radius=8, fill=dark)


def _speaker(draw, color):
    cx = CENTER_X
    dark = _lerp(color, (0, 0, 0), 0.35)
    draw.rounded_rectangle((cx - 100, 165, cx + 100, 415), radius=46, fill=color)
    draw.rounded_rectangle((cx - 100, 165, cx + 100, 225), radius=20, fill=dark)
    draw.rounded_rectangle((cx - 100, 355, cx + 100, 415), radius=20, fill=dark)
    for gy in range(245, 360, 24):
        for gx in range(-70, 75, 24):
            draw.ellipse(
                (cx + gx - 5, gy - 5, cx + gx + 5, gy + 5), fill=_lerp(color, (0, 0, 0), 0.45)
            )
    draw.rounded_rectangle((cx - 30, 425, cx - 12, 440), radius=4, fill=dark)
    draw.rounded_rectangle((cx + 12, 425, cx + 30, 440), radius=4, fill=dark)


def _mug(draw, color):
    cx = CENTER_X
    dark = _lerp(color, (0, 0, 0), 0.35)
    light = _lerp(color, (255, 255, 255), 0.5)
    draw.arc((cx + 68, 200, cx + 150, 330), start=-60, end=120, fill=color, width=18)
    draw.rounded_rectangle((cx - 95, 210, cx + 95, 380), radius=26, fill=light)
    draw.rounded_rectangle((cx - 100, 178, cx + 100, 216), radius=14, fill=dark)
    draw.rounded_rectangle((cx - 16, 162, cx + 16, 180), radius=8, fill=dark)
    draw.ellipse((cx - 40, 260, cx + 0, 300), fill=(255, 255, 255, 255))
    draw.ellipse((cx - 18, 240, cx + 26, 286), fill=(255, 255, 255, 255))
    draw.rounded_rectangle((cx - 40, 272, cx + 26, 300), radius=10, fill=(255, 255, 255, 255))
    for dx in (-18, 0, 18):
        draw.arc((cx + dx - 10, 120, cx + dx + 10, 160), start=200, end=340, fill=(255, 255, 255, 160), width=6)


def _generic(draw, color, name):
    cx = CENTER_X
    draw.rounded_rectangle((cx - 110, 200, cx + 110, 380), radius=24, fill=_lerp(color, (0, 0, 0), 0.2))
    draw.rounded_rectangle((cx - 90, 220, cx + 90, 360), radius=16, fill=_lerp(color, (255, 255, 255), 0.3))


_KIND_DRAWERS = (
    ('smartphone', _smartphone),
    ('fone', _headphone),
    ('mochila', _backpack),
    ('relogio', _watch),
    ('relógio', _watch),
    ('caixa', _speaker),
    ('caneca', _mug),
)


def make_product_image(name, color):
    color = _hex_to_rgb(color)
    canvas = _background(color).convert('RGBA')

    name_key = name.lower()
    drawer = _generic
    for key, func in _KIND_DRAWERS:
        if key in name_key:
            drawer = func
            break

    _floor_shadow(canvas, half_width=190, y=470)
    draw = ImageDraw.Draw(canvas)
    if drawer is _generic:
        drawer(draw, color, name)
    else:
        drawer(draw, color)
    _draw_name(canvas, name)
    _draw_watermark(draw)

    buffer = io.BytesIO()
    canvas.convert('RGB').save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())
