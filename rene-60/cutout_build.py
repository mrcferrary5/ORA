import sys
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from scipy import ndimage
from rembg import remove, new_session
src, out = sys.argv[1], sys.argv[2]
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB").crop((470, 1200, 910, 2300))
res = remove(im, session=new_session("u2net_human_seg"), alpha_matting=True,
             alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=20, alpha_matting_erode_size=8)
a = np.asarray(res.split()[-1]).astype(np.float32)
lab, n = ndimage.label(a > 128)
sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
keep = lab == (np.argmax(sizes) + 1)
keep = ndimage.binary_fill_holes(ndimage.binary_closing(keep, iterations=2))
a = np.where(keep, a, 0)
a = ndimage.gaussian_filter(a, 0.6)
res.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
pad = 40
res = ImageOps.expand(res, pad, fill=(0, 0, 0, 0))
m = np.asarray(res.split()[-1]) > 100
dist = ndimage.distance_transform_edt(~m)
edge = ndimage.gaussian_filter((dist <= 12).astype(np.float32), 1.2)
base = Image.new("RGBA", res.size, (255, 250, 243, 0)); base.putalpha(Image.fromarray((np.clip(edge * 1.6, 0, 1) * 255).astype(np.uint8)))
outimg = Image.alpha_composite(base, res)
outimg = outimg.crop(outimg.getbbox())
outimg.save(out, "WEBP", quality=86, method=6)
print(outimg.size)
