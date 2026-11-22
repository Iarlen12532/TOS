import os, sys
from PIL import Image, ImageDraw, ImageFilter

S = 1024
T_STROKES = [
    ((205, 340), (390, 235), (650, 245), (830, 305), 30, 64),
    ((540, 255), (440, 430), (610, 610), (505, 790), 74, 50),
    ((505, 790), (470, 860), (360, 880), (322, 810), 50, 26),
    ((322, 810), (298, 765), (345, 735), (372, 765), 26, 18),
]

def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
            u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])

def draw_t(d, color, dx=0, dy=0):
    for p0, p1, p2, p3, w0, w1 in T_STROKES:
        for i in range(221):
            t = i / 220
            x, y = bezier(p0, p1, p2, p3, t)
            r = (w0 + (w1 - w0) * t) / 2
            d.ellipse((x+dx-r, y+dy-r, x+dx+r, y+dy+r), fill=color)

def gradient(top, bottom):
    img = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(img)
    for y in range(S):
        k = y / (S - 1)
        d.line((0, y, S, y), fill=tuple(int(top[i]+(bottom[i]-top[i])*k) for i in range(3)))
    return img

def squircle_mask(n=4.5):
    big = S * 2
    m = Image.new("L", (big, big), 0)
    px = m.load()
    c = (big - 1) / 2
    for y in range(big):
        for x in range(big):
            if abs((x-c)/c)**n + abs((y-c)/c)**n <= 1:
                px[x, y] = 255
    return m.resize((S, S), Image.LANCZOS)

def make_icon():
    bg = gradient((35, 163, 232), (3, 58, 114))
    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).ellipse((-300, -400, 700, 450), fill=70)
    bg.paste((255, 255, 255), mask=glow.filter(ImageFilter.GaussianBlur(90)))
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw_t(ImageDraw.Draw(shadow), (0, 20, 50, 150), 10, 18)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    letter = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw_t(ImageDraw.Draw(letter), (255, 255, 255, 255))
    icon = bg.convert("RGBA")
    icon.alpha_composite(shadow)
    icon.alpha_composite(letter)
    icon.putalpha(squircle_mask())
    return icon

icon = make_icon()
changed = 0
for root, _, files in os.walk(sys.argv[1]):
    for name in files:
        path = os.path.join(root, name)
        if name.startswith("ic_launcher") and name.endswith(".png"):
            with Image.open(path) as old:
                w, h = old.size
            icon.resize((w, h), Image.LANCZOS).save(path)
            print("icone trocado:", path, w, h)
            changed += 1
        elif name.startswith("ic_launcher") and name.endswith(".xml") and "anydpi" in root:
            os.remove(path)
            print("xml adaptativo removido:", path)
print("total de PNGs trocados:", changed)
