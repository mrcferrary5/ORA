"""Genera las piezas del collage (recortes con borde blanco, semitono, bastones, estrellas, guirnalda...).

Uso:  python assets_build.py <carpeta_con_fotos_originales>
Requiere: pillow, numpy, scipy, rembg
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy import ndimage
from scipy.spatial import cKDTree

SRC = Path(sys.argv[1])
OUT = Path(__file__).parent / "collage"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(60)


# ---------------------------------------------------------------- helpers
def screen(h, w, cell=6.0, angle=45):
    """Dot-screen value in [0,1] per pixel (distance to nearest dot centre)."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle)
    u = (x * math.cos(a) + y * math.sin(a)) / cell
    v = (-x * math.sin(a) + y * math.cos(a)) / cell
    du = u - np.round(u)
    dv = v - np.round(v)
    return np.sqrt(du * du + dv * dv) / 0.7071  # 0 centre .. 1 corner


def halftone_gray(rgb, cell=5.0, contrast=1.25):
    g = np.asarray(rgb.convert("L"), np.float32) / 255
    g = np.clip((g - 0.5) * contrast + 0.5, 0, 1)
    dark = 1 - g
    d = screen(*g.shape, cell=cell)
    r = np.sqrt(dark) * 1.05
    ink = np.clip((r - d) * 6 + 0.5, 0, 1)
    out = (1 - ink) * 245 + ink * 18
    return Image.fromarray(out.astype(np.uint8)).convert("RGB")


def halftone_color(rgb, cell=4.0, amount=0.22):
    a = np.asarray(rgb, np.float32) / 255
    lum = a.mean(axis=2)
    d = screen(*lum.shape, cell=cell)
    r = np.sqrt(np.clip(1 - lum, 0, 1))
    ink = np.clip((r - d) * 5 + 0.5, 0, 1)[..., None]
    out = a * (1 - amount) + a * a * amount * 1.4 * ink + a * amount * (1 - ink) * 1.0
    return Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8))


def sticker(rgba, border=14, rough=True):
    """Add a white cut-paper border around an RGBA cut-out."""
    rgba = rgba.convert("RGBA")
    pad = border * 3
    rgba = ImageOps.expand(rgba, pad, fill=(0, 0, 0, 0))
    al = np.asarray(rgba.split()[-1]) > 110
    dist = ndimage.distance_transform_edt(~al)
    lim = border
    if rough:
        n = ndimage.gaussian_filter(rng.standard_normal(al.shape), 6)
        n = n / (np.abs(n).max() + 1e-6)
        lim = border * (1 + 0.35 * n)
    edge = dist <= lim
    edge = ndimage.binary_closing(edge, iterations=3)
    base = Image.new("RGBA", rgba.size, (255, 255, 255, 0))
    base.putalpha(Image.fromarray((edge * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    base = Image.alpha_composite(base, rgba)
    bbox = base.getbbox()
    return base.crop(bbox)


def cutout(img, model):
    from rembg import remove, new_session
    s = new_session(model)
    res = remove(img, session=s, post_process_mask=True)
    a = np.asarray(res.split()[-1]).astype(np.float32)
    a = ndimage.gaussian_filter(a, 1.0)
    a = np.clip((a - 90) * 2.2, 0, 255)
    lab, n = ndimage.label(a > 128)
    if n > 1:  # keep the largest blob(s) only
        sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
        keep = np.isin(lab, [i + 1 for i, s_ in enumerate(sizes) if s_ > sizes.max() * 0.15])
        a = a * keep
    res.putalpha(Image.fromarray(a.astype(np.uint8)))
    return res


def save(img, name, q=82):
    img.save(OUT / f"{name}.webp", "WEBP", quality=q, method=6)
    print(name, img.size)


def load(name):
    return ImageOps.exif_transpose(Image.open(SRC / name)).convert("RGB")


# ---------------------------------------------------------------- René cut-outs
def rene(name, box, height, model="u2net_human_seg", mode="color", border=16, exclude=()):
    im = load(name).crop(box)
    im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
    cut = cutout(im, model)
    if exclude:
        m = Image.new("L", cut.size, 255)
        md = ImageDraw.Draw(m)
        for poly in exclude:
            md.polygon([(x * cut.width, y * cut.height) for x, y in poly], fill=0)
        a = np.asarray(cut.split()[-1]).astype(np.float32) * (np.asarray(m) / 255)
        lab, n = ndimage.label(a > 128)
        if n > 1:
            sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
            a = a * (lab == (np.argmax(sizes) + 1))
        cut.putalpha(Image.fromarray(a.astype(np.uint8)))
    rgb = cut.convert("RGB")
    rgb = ImageOps.autocontrast(rgb, cutoff=1)
    rgb = halftone_color(rgb) if mode == "color" else halftone_gray(rgb, cell=4.2)
    rgb.putalpha(cut.split()[-1])
    return sticker(rgb, border=border)


save(rene("f3cbec50-image.jpg", (660, 150, 1540, 1720), 1100, exclude=[
    [(0, 0), (0.2, 0), (0.2, 0.33), (0.17, 0.47), (0.13, 0.6), (0.06, 0.76), (0, 0.76)],
    [(0.68, 0.2), (1, 0.2), (1, 0.4), (0.68, 0.345)]]), "rene-gala")
save(rene("3a92ee36-image.jpg", (1150, 1090, 1800, 1780), 700, exclude=[[(0, 0.3), (0.14, 0.3), (0.14, 1), (0, 1)]]), "rene-pijama")
save(rene("a5e47b0f-image.jpg", (110, 360, 870, 1180), 860), "rene-sombrero")
save(rene("bb4d1775-image.jpg", (0, 0, 1932, 2420), 1000, model="u2net"), "rene-perrito")

save(rene("57c34bd2-image.jpg", (219, 953, 1546, 2421), 1100), "rene-chaqueta")
save(rene("9843a93e-image.jpg", (300, 290, 1840, 2576), 1000, model="u2net"), "rene-pastel")
save(rene("2f29c5e7-image.jpg", (0, 930, 1159, 2563), 1000), "rene-mascarilla")
save(rene("6865ef12-image.jpg", (520, 1250, 860, 2240), 900), "rene-brazos")

# 90s print: rectangular halftone photo with torn white edge
p = load("cd0ae850-image.jpg").crop((640, 0, 960, 400)).resize((560, 700), Image.LANCZOS)
p = halftone_color(ImageOps.autocontrast(p, 1), cell=3.6, amount=0.3).convert("RGBA")
save(sticker(p, border=18), "rene-90s")


# ---------------------------------------------------------------- disco ball
def disco(size=900):
    h = w = size
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    R = size / 2 - 4
    nx = (x - w / 2) / R
    ny = (y - h / 2) / R
    rr = nx * nx + ny * ny
    inside = rr <= 1
    nz = np.sqrt(np.clip(1 - rr, 0, 1))
    lat = np.arcsin(np.clip(ny, -1, 1))
    lon = np.arctan2(nx, nz) + 0.4
    bands = 34
    bi = np.floor((lat + math.pi / 2) / math.pi * bands)
    latc = (bi + 0.5) / bands * math.pi - math.pi / 2
    M = np.maximum(6, np.round(2 * bands * np.cos(latc)))
    fj = (lon + math.pi) / (2 * math.pi) * M
    bj = np.floor(fj)
    fu = fj - bj
    fv = (lat + math.pi / 2) / math.pi * bands - bi
    grout = (fu < 0.09) | (fu > 0.91) | (fv < 0.09) | (fv > 0.91)
    hsh = np.sin(bi * 127.1 + bj * 311.7) * 43758.5453
    hsh = hsh - np.floor(hsh)
    # facet-centre normal for reflections
    lonc = (bj + 0.5) / M * 2 * math.pi - math.pi
    fnx = np.cos(latc) * np.sin(lonc)
    fny = np.sin(latc)
    fnz = np.cos(latc) * np.cos(lonc)
    val = 0.42 + 0.5 * hsh ** 1.6
    for lx, ly, lz, k in [(-0.5, -0.55, 0.67, 1.0), (0.55, 0.2, 0.8, 0.8), (-0.1, 0.6, 0.8, 0.6)]:
        dd = (fnx - lx) ** 2 + (fny - ly) ** 2 + (fnz - lz) ** 2
        val += k * np.exp(-dd / 0.025)
    val *= 0.7 + 0.3 * nz
    val = np.where(grout, val * 0.25, val)
    val = np.clip(val, 0, 1)
    img = Image.fromarray((val * 255).astype(np.uint8)).convert("RGB")
    img = halftone_gray(img, cell=4.2, contrast=1.0)
    a = Image.fromarray((inside * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    img.putalpha(a)
    # star glints
    d = ImageDraw.Draw(img)
    for gx, gy, s in [(0.3, 0.27, 70), (0.62, 0.55, 46), (0.4, 0.75, 34), (0.75, 0.3, 30)]:
        cx, cy = gx * w, gy * h
        for wdt, alpha in [(9, 90), (4, 255)]:
            d.line([(cx - s, cy), (cx + s, cy)], fill=(255, 255, 255, alpha), width=wdt)
            d.line([(cx, cy - s), (cx, cy + s)], fill=(255, 255, 255, alpha), width=wdt)
    return sticker(img, border=16, rough=False)


save(disco(), "disco", q=80)


# ---------------------------------------------------------------- candy cane
def candy(w=420, h=1100, r=34):
    cx, top, hook = w * 0.68, h * 0.24, w * 0.28
    pts = [(cx, yy) for yy in np.linspace(h - r - 6, top, 600)]
    for t in np.linspace(0, math.pi, 260):  # over the top, to the left
        pts.append((cx - hook + hook * math.cos(t), top - hook * math.sin(t)))
    for yy in np.linspace(top, top + hook * 0.7, 60):
        pts.append((cx - 2 * hook, yy))
    P = np.array(pts, np.float32)
    seg = np.sqrt((np.diff(P, axis=0) ** 2).sum(1))
    S = np.concatenate([[0], np.cumsum(seg)])
    tree = cKDTree(P)
    y, x = np.mgrid[0:h, 0:w]
    q = np.stack([x.ravel(), y.ravel()], 1).astype(np.float32)
    dist, idx = tree.query(q, distance_upper_bound=r + 2)
    ok = np.isfinite(dist)
    out = np.zeros((h * w, 4), np.float32)
    i2 = np.clip(idx[ok], 1, len(P) - 2)
    tang = P[i2 + 1] - P[i2 - 1]
    tang /= np.linalg.norm(tang, axis=1, keepdims=True)
    rel = q[ok] - P[i2]
    side = np.sign(tang[:, 0] * rel[:, 1] - tang[:, 1] * rel[:, 0])
    dd = np.clip(dist[ok] / r, 0, 1) * side
    s = S[i2]
    phase = ((s + dd * r * 0.9) / 46.0) % 2
    red = phase < 0.85
    base = np.where(red[:, None], np.array([0.80, 0.07, 0.13]), np.array([0.98, 0.96, 0.94]))
    shade = np.sqrt(np.clip(1 - dd ** 2, 0, 1))
    col = base * (0.45 + 0.55 * shade[:, None]) + 0.35 * np.exp(-((dd + 0.4) ** 2) / 0.02)[:, None]
    out[ok, :3] = np.clip(col, 0, 1)
    out[ok, 3] = np.clip((r + 1 - dist[ok]), 0, 1)
    img = Image.fromarray((out.reshape(h, w, 4) * 255).astype(np.uint8), "RGBA")
    rgb = halftone_color(img.convert("RGB"), cell=3.5, amount=0.18)
    rgb.putalpha(img.split()[-1])
    return sticker(rgb, border=12, rough=False)


save(candy(), "candy")


# ---------------------------------------------------------------- glitter star
def star(size=300):
    big = size * 2
    m = Image.new("L", (big, big), 0)
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rad = big * (0.48 if k % 2 == 0 else 0.2)
        pts.append((big / 2 + rad * math.cos(ang), big / 2 + rad * math.sin(ang)))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    g = rng.random((size // 2, size // 2))
    g = np.kron(g, np.ones((2, 2)))[:size, :size]
    sp = rng.random((size, size)) > 0.985
    lo, hi = np.array([0.45, 0.31, 0.07]), np.array([1.0, 0.86, 0.45])
    c = lo + (hi - lo) * (g[..., None] ** 1.4)
    c[sp] = [1, 0.98, 0.85]
    img = Image.fromarray((c * 255).astype(np.uint8))
    img.putalpha(m)
    return img


save(star(), "star")


# ---------------------------------------------------------------- pine garland
def garland(w=1800, h=380):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    greens = [(16, 52, 30), (24, 74, 40), (36, 96, 52), (52, 112, 60), (12, 40, 24), (70, 128, 70)]
    for layer in range(3):
        for bx in np.linspace(-80, w + 80, 40 + layer * 10):
            by = 40 + layer * 40 + rng.uniform(-20, 30)
            ang0 = math.radians(rng.uniform(60, 120))
            L = rng.uniform(140, 230)
            for t in np.linspace(0, 1, 70):
                px = bx + math.cos(ang0) * L * t
                py = by + math.sin(ang0) * L * t
                for _ in range(7):
                    a = ang0 + rng.choice([-1, 1]) * math.radians(rng.uniform(25, 70))
                    nl = rng.uniform(16, 34) * (1 - 0.5 * t)
                    col = tuple(int(v * (0.6 + 0.2 * layer)) for v in greens[rng.integers(len(greens))]) + (255,)
                    d.line([(px, py), (px + math.cos(a) * nl, py + math.sin(a) * nl)], fill=col, width=2)
    # lights
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    dots = []
    for x in np.linspace(20, w - 20, 34):
        y = 70 + 60 * math.sin(x / 140) + rng.uniform(-30, 40)
        dots.append((x + rng.uniform(-20, 20), y))
    for x, y in dots:
        gd.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(255, 210, 120, 150))
    glow = glow.filter(ImageFilter.GaussianBlur(9))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)
    for x, y in dots:
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 246, 214, 255))
    img = img.filter(ImageFilter.UnsharpMask(2, 60))
    return img


save(garland(), "garland", q=80)


# ---------------------------------------------------------------- poinsettia
def leaf(d, cx, cy, ang, L, W, col, vein):
    pts = []
    for t in np.linspace(0, 1, 40):
        wid = W * math.sin(math.pi * t) ** 0.9 * (1 - 0.25 * t)
        pts.append((t * L, wid))
    pts += [(x, -y) for x, y in pts[::-1]]
    ca, sa = math.cos(ang), math.sin(ang)
    P = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]
    d.polygon(P, fill=col)
    d.line([(cx, cy), (cx + L * 0.92 * ca, cy + L * 0.92 * sa)], fill=vein, width=3)
    for t in (0.3, 0.5, 0.7):
        bx, by = cx + L * t * ca, cy + L * t * sa
        for sgn in (-1, 1):
            a2 = ang + sgn * 0.6
            d.line([(bx, by), (bx + L * 0.18 * math.cos(a2), by + L * 0.18 * math.sin(a2))], fill=vein, width=2)


def poinsettia(size=800):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    for k in range(6):
        leaf(d, c, c, k * math.pi / 3 + 0.5, size * 0.47, size * 0.11, (34, 92, 48, 255), (20, 60, 30, 255))
    for k in range(7):
        leaf(d, c, c, k * 2 * math.pi / 7, size * 0.42, size * 0.10, (176, 18, 36, 255), (120, 8, 22, 255))
    for k in range(6):
        leaf(d, c, c, k * math.pi / 3 + 0.3, size * 0.28, size * 0.08, (214, 40, 56, 255), (150, 14, 30, 255))
    for k in range(9):
        a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0, size * 0.04)
        x, y = c + rr * math.cos(a), c + rr * math.sin(a)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(196, 170, 40, 255), outline=(90, 110, 30, 255), width=2)
    al = img.split()[-1]
    rgb = halftone_color(img.convert("RGB").filter(ImageFilter.GaussianBlur(1.2)), cell=5.5, amount=0.7)
    rgb.putalpha(al)
    return rgb


save(poinsettia(), "poinsettia")


# ---------------------------------------------------------------- striped paper background
def stripes(w=720, h=1280, n=10):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    wob = 2.2 * np.sin(y / h * 2 * math.pi * 2 + x / w * 9) + 1.2 * np.sin(y / h * 2 * math.pi * 5 + x / w * 3)
    ph = ((x + wob) / (w / n)) % 1
    band = ph < 0.5
    edge = np.clip(np.minimum(np.abs(ph - 0.5), np.minimum(ph, 1 - ph)) * (w / n) / 2.5, 0, 1)
    c1, c2 = np.array([204, 40, 44]), np.array([186, 30, 38])
    base = np.where(band[..., None], c1, c2).astype(np.float32)
    base = base * (0.9 + 0.1 * edge[..., None])
    fib = ndimage.gaussian_filter(rng.standard_normal((h, w)), (6, 0.8))
    fib = fib / np.abs(fib).max()
    grain = rng.standard_normal((h, w)) * 4
    base += (fib * 9 + grain)[..., None]
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


stripes().save(OUT / "stripes.jpg", quality=80)
print("stripes")
