from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"
OUT_ROOT = ROOT / "assets" / "perf" / "optimized"
ICON_OUT = OUT_ROOT / "icons"
OUT_ROOT.mkdir(parents=True, exist_ok=True)
ICON_OUT.mkdir(parents=True, exist_ok=True)

def prepare_image(path: Path):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    if "A" in im.getbands():
        if im.mode != "RGBA":
            im = im.convert("RGBA")
    elif im.mode != "RGB":
        im = im.convert("RGB")
    return im

def save_resized(src_rel: str, dst_rel: str, max_w: int, max_h: int | None = None, quality: int = 82):
    src = ROOT / src_rel
    dst = ROOT / dst_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = prepare_image(src)
    original_size = im.size
    if max_h is None:
        max_h = 10000
    im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    im.save(dst, "WEBP", quality=quality, method=6)
    print(f"{src_rel}: {original_size[0]}x{original_size[1]} -> {im.size[0]}x{im.size[1]}, {src.stat().st_size} -> {dst.stat().st_size} bytes")
    return original_size, im.size

# Responsive above-the-fold variants: originals remain untouched as desktop fallbacks.
hero_original, hero_mobile = save_resized(
    "assets/perf/hero.webp",
    "assets/perf/optimized/hero-mobile.webp",
    max_w=1000,
    quality=80,
)
logo_original, logo_small = save_resized(
    "assets/perf/logo.webp",
    "assets/perf/optimized/logo-small.webp",
    max_w=600,
    quality=82,
)

icon_sources = [
    "assets/icons_v2/location.png",
    "assets/icons_v2/car_service.png",
    "assets/icons_v2/warranty.png",
    "assets/icons_v2/tools.png",
    "assets/icons_v2/engine.png",
    "assets/icons_v2/transmission.png",
    "assets/icons_v2/suspension.png",
    "assets/icons_v2/tires.png",
    "assets/icons_v2/masters.png",
    "assets/icons_v2/prices.png",
    "assets/icons_v2/service.png",
    "assets/perf/icons/brakes.webp",
    "assets/perf/icons/steering.webp",
    "assets/perf/icons/turbo.webp",
    "assets/perf/icons/electrics.webp",
    "assets/perf/icons/wash.webp",
    "assets/perf/icons/cooling.webp",
    "assets/perf/icons/climate.webp",
    "assets/perf/icons/fuel.webp",
    "assets/perf/icons/exhaust.webp",
    "assets/perf/icons/welding.webp",
]

replacements = {}
for src_rel in icon_sources:
    src = Path(src_rel)
    dst_rel = f"assets/perf/optimized/icons/{src.stem}.webp"
    save_resized(src_rel, dst_rel, max_w=192, max_h=192, quality=82)
    replacements[src_rel] = dst_rel

html = HTML_PATH.read_text(encoding="utf-8")

old_preload = '<link rel="preload" as="image" href="assets/perf/hero.webp" type="image/webp" fetchpriority="high"/>'
new_preload = (
    '<link rel="preload" as="image" href="assets/perf/optimized/hero-mobile.webp" '
    'type="image/webp" media="(max-width:760px)" fetchpriority="high"/>\n'
    '<link rel="preload" as="image" href="assets/perf/hero.webp" '
    'type="image/webp" media="(min-width:761px)" fetchpriority="high"/>'
)
if old_preload not in html:
    raise SystemExit("Expected hero preload tag not found; refusing unsafe edit")
html = html.replace(old_preload, new_preload, 1)

old_hero = '<img alt="" src="assets/perf/hero.webp" width="1600" height="900" decoding="async" fetchpriority="high"/>'
new_hero = (
    f'<img alt="" src="assets/perf/hero.webp" '
    f'srcset="assets/perf/optimized/hero-mobile.webp {hero_mobile[0]}w, assets/perf/hero.webp {hero_original[0]}w" '
    'sizes="(max-width:760px) 100vw, 62vw" '
    'width="1600" height="900" decoding="async" fetchpriority="high"/>'
)
if old_hero not in html:
    raise SystemExit("Expected hero image tag not found; refusing unsafe edit")
html = html.replace(old_hero, new_hero, 1)

header_logo = '<img alt="КАД БОКС 778" src="assets/perf/logo.webp" width="1100" height="367" decoding="async" fetchpriority="high"/>'
header_logo_new = (
    f'<img alt="КАД БОКС 778" src="assets/perf/logo.webp" '
    f'srcset="assets/perf/optimized/logo-small.webp {logo_small[0]}w, assets/perf/logo.webp {logo_original[0]}w" '
    'sizes="(max-width:760px) 220px, 385px" '
    'width="1100" height="367" decoding="async" fetchpriority="high"/>'
)
if header_logo not in html:
    raise SystemExit("Expected header logo tag not found")
html = html.replace(header_logo, header_logo_new, 1)

footer_logo = '<img alt="КАД БОКС 778" src="assets/perf/logo.webp" width="1100" height="367" loading="lazy" decoding="async"/>'
footer_logo_new = (
    f'<img alt="КАД БОКС 778" src="assets/perf/logo.webp" '
    f'srcset="assets/perf/optimized/logo-small.webp {logo_small[0]}w, assets/perf/logo.webp {logo_original[0]}w" '
    'sizes="220px" width="1100" height="367" loading="lazy" decoding="async"/>'
)
if footer_logo not in html:
    raise SystemExit("Expected footer logo tag not found")
html = html.replace(footer_logo, footer_logo_new, 1)

for old, new in replacements.items():
    if old not in html:
        raise SystemExit(f"Expected referenced image not found in HTML: {old}")
    html = html.replace(old, new)

HTML_PATH.write_text(html, encoding="utf-8")
print("Updated index.html image references and responsive hero/logo sources.")
