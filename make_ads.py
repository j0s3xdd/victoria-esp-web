from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import cv2
from rembg import remove
import io

SIZE = 1080
FONTS = {
    'bold':    r'C:\Windows\Fonts\segoeuib.ttf',
    'semibold':r'C:\Windows\Fonts\seguisb.ttf',
    'regular': r'C:\Windows\Fonts\segoeui.ttf',
    'light':   r'C:\Windows\Fonts\segoeuil.ttf',
}

def lf(style, size):
    return ImageFont.truetype(FONTS[style], size)

def smart_crop(path, top_offset=0):
    img = Image.open(path).convert('RGB')
    w, h = img.size
    left = (w - SIZE) // 2
    img = img.crop((left, top_offset, left + SIZE, top_offset + SIZE))
    return img.resize((SIZE, SIZE), Image.LANCZOS)

def grade_warm(img, brightness=1.08, contrast=1.06, saturation=1.10, warmth=1.06):
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(saturation)
    r, g, b = img.split()
    r = r.point(lambda x: min(255, int(x * warmth)))
    b = b.point(lambda x: int(x * 0.96))
    return Image.merge('RGB', (r, g, b))

def grade_cool_authority(img, brightness=1.06, contrast=1.10, saturation=0.95):
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(saturation)
    return img

def brighten_face_zone(img, zone_top=0.05, zone_bot=0.65, strength=0.20):
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]
    cy = int(h * (zone_top + zone_bot) / 2)
    cx = w // 2
    ry = int(h * (zone_bot - zone_top) / 2)
    rx = int(w * 0.52)
    Y, X = np.ogrid[:h, :w]
    ellipse = ((X - cx)/rx)**2 + ((Y - cy)/ry)**2
    mask = np.clip(1 - ellipse, 0, 1)**0.5 * strength
    arr = np.clip(arr * (1 + mask[:, :, None]), 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def vignette(img, strength=0.40):
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]
    cy, cx = h/2, w/2
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((X-cx)**2 + (Y-cy)**2)
    v = 1 - strength * (dist / np.sqrt(cx**2 + cy**2))**1.8
    v = np.clip(v, 0, 1)
    arr = np.clip(arr * v[:,:,None], 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def gradient_overlay(img, color_rgb, top_frac=0.13, bot_frac=0.44):
    w, h = img.size
    ov = Image.new('RGBA', (w, h), (0,0,0,0))
    d = ImageDraw.Draw(ov)
    r, g, b = color_rgb
    tp = int(h * top_frac)
    for y in range(tp):
        a = int(155 * (1 - y/tp)**1.3)
        d.line([(0,y),(w,y)], fill=(r,g,b,a))
    bs = int(h * (1 - bot_frac))
    for y in range(bs, h):
        t = (y - bs) / (h - bs)
        a = int(235 * t**1.3)
        d.line([(0,y),(w,y)], fill=(r,g,b,a))
    return Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')

def shadowed_text(img, text, font, center_y, fill=(255,255,255), max_w=930):
    dummy = ImageDraw.Draw(img)
    words = text.split()
    lines, cur = [], []
    for word in words:
        test = ' '.join(cur + [word])
        bx = dummy.textbbox((0,0), test, font=font)
        if (bx[2]-bx[0]) > max_w and cur:
            lines.append(' '.join(cur)); cur = [word]
        else:
            cur.append(word)
    if cur:
        lines.append(' '.join(cur))
    lh = dummy.textbbox((0,0),'Ag',font=font)[3] + 18
    total = len(lines) * lh
    y = center_y - total // 2
    for line in lines:
        bx = dummy.textbbox((0,0), line, font=font)
        tw = bx[2] - bx[0]
        x = (SIZE - tw) // 2
        sh = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
        ImageDraw.Draw(sh).text((x+2, y+4), line, font=font, fill=(0,0,0,180))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        img = Image.alpha_composite(img.convert('RGBA'), sh).convert('RGB')
        dummy = ImageDraw.Draw(img)
        dummy.text((x, y), line, font=font, fill=fill)
        y += lh
    return img, y

def brand_header(img, cream=(248,243,233), gold=(201,169,110)):
    d = ImageDraw.Draw(img)
    fn = lf('light', 28)
    ft = lf('light', 18)
    name = 'VICTORIA'
    tag  = 'especialista en alimentación'
    bx = d.textbbox((0,0), name, font=fn)
    d.text(((SIZE-(bx[2]-bx[0]))//2, 30), name, font=fn, fill=cream)
    d.line([(SIZE//2-40, 68),(SIZE//2+40, 68)], fill=gold, width=1)
    bx2 = d.textbbox((0,0), tag, font=ft)
    d.text(((SIZE-(bx2[2]-bx2[0]))//2, 76), tag, font=ft, fill=cream)
    return img

def pro_background(subject_path):
    print("  Removing background with AI...")
    with open(subject_path, 'rb') as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)
    subject = Image.open(io.BytesIO(output_bytes)).convert('RGBA')

    # Find subject bounding box from alpha channel
    alpha_arr = np.array(subject.split()[3])
    rows = np.any(alpha_arr > 15, axis=1)
    cols = np.any(alpha_arr > 15, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    subj_h = rmax - rmin
    subj_w = cmax - cmin

    # Scale subject so it fills ~85% of frame height
    scale = (SIZE * 0.85) / subj_h
    new_w = int(subject.width * scale)
    new_h = int(subject.height * scale)
    subject = subject.resize((new_w, new_h), Image.LANCZOS)

    # Recalculate bounding box after scale
    new_rmin = int(rmin * scale)
    new_cmin = int(cmin * scale)
    new_cmax = int(cmax * scale)
    new_rmax = int(rmax * scale)
    subj_cx = (new_cmin + new_cmax) // 2
    subj_top = new_rmin

    # Position: center horizontally, slight left of center (visual balance with text)
    paste_x = (SIZE // 2) - subj_cx + 30
    paste_y = int(SIZE * 0.02) - subj_top  # start near top

    # Deep forest green studio gradient background
    bg = Image.new('RGB', (SIZE, SIZE))
    bg_draw = ImageDraw.Draw(bg)
    for y in range(SIZE):
        t = y / SIZE
        rv = int(22 + (35-22)*t)
        gv = int(38 + (60-38)*t)
        bv = int(28 + (45-28)*t)
        bg_draw.line([(0,y),(SIZE,y)], fill=(rv, gv, bv))

    # Ambient glow behind head — position it where head will be
    head_cx = (SIZE // 2) + 30
    head_cy = int(SIZE * 0.25)
    glow = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for radius in range(220, 0, -4):
        alpha_val = int(18 * (1 - radius/220)**0.8)
        gd.ellipse([(head_cx-radius, head_cy-radius//2),
                    (head_cx+radius, head_cy+int(radius*1.2))],
                   fill=(55, 95, 70, alpha_val))
    bg = Image.alpha_composite(bg.convert('RGBA'), glow).convert('RGB')

    # Paste subject — clip to canvas
    paste_x = max(-new_w//4, min(paste_x, SIZE - new_w + new_w//4))
    paste_y = max(-50, paste_y)
    bg.paste(subject, (paste_x, paste_y), mask=subject.split()[3])
    return bg

def build_ad1(foto_path, out_path):
    print("Building Ad 1 - Emotional...")
    img = smart_crop(foto_path)
    img = grade_warm(img)
    img = brighten_face_zone(img)
    img = vignette(img, 0.38)
    img = gradient_overlay(img, (18, 34, 24))
    img = brand_header(img)

    font_h   = lf('bold', 66)
    font_sub = lf('semibold', 29)
    cream = (248, 243, 233)
    gold  = (201, 169, 110)

    img, text_bot = shadowed_text(img, '¿Cuánto tiempo llevas sin reconocerte?',
                                  font_h, int(SIZE*0.775), cream)
    d = ImageDraw.Draw(img)
    sep_y = text_bot + 18
    d.line([(SIZE//2-80, sep_y),(SIZE//2+80, sep_y)], fill=gold, width=1)
    sub = 'RESET 45  ·  5 días  ·  49 €'
    bx = d.textbbox((0,0), sub, font=font_sub)
    d.text(((SIZE-(bx[2]-bx[0]))//2, sep_y+14), sub, font=font_sub, fill=gold)

    img.save(out_path, 'JPEG', quality=96, optimize=True)
    print(f"  Saved: {out_path}")

def build_ad2(foto_path, out_path):
    print("Building Ad 2 - Authority (AI background removal)...")
    img = pro_background(foto_path)
    img = grade_cool_authority(img)
    img = vignette(img, 0.28)
    img = gradient_overlay(img, (12, 18, 28))
    img = brand_header(img, cream=(248,243,233), gold=(185,162,128))

    font_h   = lf('bold', 66)
    font_sub = lf('semibold', 29)
    cream = (248, 243, 233)
    gold  = (185, 162, 128)

    img, text_bot = shadowed_text(img, 'Lo has probado todo. Esto es diferente.',
                                  font_h, int(SIZE*0.775), cream)
    d = ImageDraw.Draw(img)
    sep_y = text_bot + 18
    d.line([(SIZE//2-80, sep_y),(SIZE//2+80, sep_y)], fill=gold, width=1)
    sub = 'Especialista en alimentación · Mujeres 45-65 años'
    bx = d.textbbox((0,0), sub, font=font_sub)
    d.text(((SIZE-(bx[2]-bx[0]))//2, sep_y+14), sub, font=font_sub, fill=gold)

    img.save(out_path, 'JPEG', quality=96, optimize=True)
    print(f"  Saved: {out_path}")

FOTO1 = r'C:\Users\romer\Downloads\WhatsApp Image 2026-05-06 at 7.24.13 PM.jpeg'
FOTO2 = r'C:\Users\romer\Downloads\WhatsApp Image 2026-05-06 at 7.19.35 PM.jpeg'

build_ad1(FOTO1, r'C:\Users\romer\Desktop\anuncio_1_final.jpg')
build_ad2(FOTO2, r'C:\Users\romer\Desktop\anuncio_2_final.jpg')
print("\nDone.")
