"""Bolas disco fotorrealistas (reflejo de un cuarto oscuro con luces de colores).
Uso: python disco_build.py"""
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).parent / "collage"


def ball(name, lights, size=900, bands=42, seed=1, base=(0.05, 0.05, 0.07)):
    rng = np.random.default_rng(seed)
    h = w = size
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    R = size / 2 - 2
    nx, ny = (x - w / 2) / R, (y - h / 2) / R
    rr = nx * nx + ny * ny
    inside = rr <= 1
    nz = np.sqrt(np.clip(1 - rr, 0, 1))
    lat = np.arcsin(np.clip(ny, -1, 1))
    lon = np.arctan2(nx, nz) + 0.35
    bi = np.floor((lat + math.pi / 2) / math.pi * bands)
    latc = (bi + 0.5) / bands * math.pi - math.pi / 2
    M = np.maximum(6, np.round(2 * bands * np.cos(latc)))
    fj = (lon + math.pi) / (2 * math.pi) * M
    bj = np.floor(fj)
    fu, fv = fj - bj, (lat + math.pi / 2) / math.pi * bands - bi
    grout = (fu < .05) | (fu > .95) | (fv < .05) | (fv > .95)
    hsh = np.sin(bi * 127.1 + bj * 311.7) * 43758.5453
    hsh -= np.floor(hsh)
    hsh2 = np.sin(bi * 269.5 + bj * 183.3) * 24634.6345
    hsh2 -= np.floor(hsh2)
    lonc = (bj + .5) / M * 2 * math.pi - math.pi - 0.35
    jit = (hsh - .5) * .12
    fnx = np.cos(latc) * np.sin(lonc + jit)
    fny = np.sin(latc + (hsh2 - .5) * .12)
    fnz = np.cos(latc) * np.cos(lonc + jit)
    # reflect view (0,0,1)
    d = fnz
    rx, ry, rz = 2 * d * fnx, 2 * d * fny, 2 * d * fnz - 1
    col = np.zeros((h, w, 3), np.float32) + np.array(base, np.float32) * 3 + .12
    # soft room gradient: brighter "ceiling"
    col += (np.clip(-ry, 0, 1) ** 2)[..., None] * np.array([.10, .09, .12])
    # many small room lights so most tiles catch something
    pal = [l[3] for l in lights] + [(1, 1, 1)] * 3
    extra = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(.1, 1), pal[rng.integers(len(pal))], rng.uniform(.5, 1.3), rng.uniform(.004, .02)) for _ in range(70)]
    for (lx, ly, lz, c, k, s) in list(lights) + extra:
        n = math.sqrt(lx * lx + ly * ly + lz * lz)
        dd = (rx - lx / n) ** 2 + (ry - ly / n) ** 2 + (rz - lz / n) ** 2
        col += np.exp(-dd / s)[..., None] * np.array(c, np.float32) * k
    col *= (0.25 + 1.5 * hsh2 ** 1.5)[..., None]           # tile-to-tile variance
    col *= (0.35 + 0.65 * nz ** .7)[..., None]            # edge falloff
    col = np.where(grout[..., None], col * .18 + .02, col)
    col = 1 - np.exp(-col * 1.6)                    # tone map
    img = Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8))
    a = Image.fromarray((inside * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8))
    img.putalpha(a)
    # glints on the brightest facets
    lum = col.mean(2) * inside
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    idx = np.argsort(lum.ravel())[::-1]
    picked = []
    for i in idx[:4000:40]:
        py, px = divmod(int(i), w)
        if all((px - qx) ** 2 + (py - qy) ** 2 > (size * .16) ** 2 for qx, qy in picked):
            picked.append((px, py))
        if len(picked) >= 4:
            break
    for k, (px, py) in enumerate(picked):
        sz = size * (.12 if k == 0 else .07)
        gd.ellipse([px - sz * .35, py - sz * .35, px + sz * .35, py + sz * .35], fill=(255, 255, 255, 70))
        for wdt, al in ((5, 120), (2, 255)):
            gd.line([(px - sz, py), (px + sz, py)], fill=(255, 255, 255, al), width=wdt)
            gd.line([(px, py - sz), (px, py + sz)], fill=(255, 255, 255, al), width=wdt)
    glow = glow.filter(ImageFilter.GaussianBlur(1.2))
    img = Image.alpha_composite(img, glow)
    img.save(OUT / f"{name}.webp", "WEBP", quality=84, method=6)
    print(name)


WHITE, WARM = (1.0, .97, .92), (1.0, .78, .45)
PINK, TEAL, VIOLET, RED, GOLD = (1.0, .35, .7), (.3, .9, 1.0), (.6, .4, 1.0), (1.0, .2, .25), (1.0, .75, .3)
ball("bola-plata", [(-.5, -.6, .6, WHITE, 3.2, .05), (.6, -.2, .7, WARM, 1.6, .08), (.2, .7, .6, RED, 1.2, .12), (-.8, .3, .4, WHITE, .9, .2)], seed=2)
ball("bola-color", [(-.5, -.6, .6, WHITE, 2.6, .05), (.6, -.3, .6, PINK, 2.0, .1), (-.6, .4, .6, TEAL, 1.8, .1), (.4, .6, .6, GOLD, 1.8, .1), (0, -.1, 1, VIOLET, 1.0, .25)], seed=5)
ball("bola-oro", [(-.5, -.6, .6, (1, .9, .6), 3.0, .05), (.6, -.2, .7, GOLD, 2.0, .1), (-.3, .6, .7, (1, .5, .3), 1.4, .14), (.5, .5, .6, RED, 1.0, .12)], seed=9, base=(.06, .04, .02))
