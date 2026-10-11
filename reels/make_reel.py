import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
W, H, FPS = 1080, 1920, 30
DUR = 12.0
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

BG = "#f7f4ee"; NAVY = "#162d47"; YEL = "#ffe27a"; ORA = "#e8572a"; RED = "#a4554e"; WHITE = "#ffffff"

_fc = {}
def font(size):
    if size not in _fc:
        _fc[size] = ImageFont.truetype(FONT, size)
    return _fc[size]

def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def pop(t, start, dur=0.25):
    """scale factor for a pop-in that overshoots slightly"""
    p = (t - start) / dur
    if p <= 0: return 0.0
    if p >= 1: return 1.0
    return ease_out(p) * (1 + 0.12 * math.sin(p * math.pi))

def text_block(img, lines, cx, top, size, color, scale=1.0, bold=True, highlight=None, gap=1.25):
    """draw centered lines; scale<1 animates pop-in; returns bottom y"""
    if scale <= 0: return top
    s = max(1, int(size * scale))
    f = font(s)
    d = ImageDraw.Draw(img)
    y = top + (size - s) * len(lines) * gap / 2
    for ln in lines:
        w = d.textlength(ln, font=f)
        x = cx - w / 2
        if highlight:
            pad = s * 0.18
            d.rounded_rectangle([x - pad, y - pad * 0.4, x + w + pad, y + s * 1.05 + pad * 0.4], radius=int(s * 0.15), fill=highlight)
        d.text((x, y), ln, font=f, fill=color, stroke_width=max(1, s // 28) if bold else 0, stroke_fill=color)
        y += s * gap
    return y

def card(d, box, fill=WHITE, outline=NAVY):
    d.rounded_rectangle(box, radius=36, fill=fill, outline=outline, width=5)

def frame(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # top brand line + progress bar (keeps eyes on the timeline)
    d.text((80, 230), "メルボルンのジャパレス英語", font=font(34), fill=RED, stroke_width=1, stroke_fill=RED)
    d.rectangle([80, 285, 80 + 820 * (t / DUR), 293], fill=ORA)

    if t < 2.2:
        # HOOK: question + scene, readable with sound off
        text_block(img, ["ジャパレスのレジで", "毎日聞くこの一言"], W / 2, 420, 64, NAVY, scale=pop(t, 0.0))
        s = pop(t, 0.35)
        if s:
            card(d, [110, 700, 970, 1080])
            text_block(img, ["「店内ですか？", "お持ち帰りですか？」"], W / 2, 770, 78, NAVY, scale=s)
        text_block(img, ["英語で言える？"], W / 2, 1180, 104, ORA, scale=pop(t, 0.9))
    elif t < 5.2:
        # THINK: 3-second countdown -> viewers stay to check their answer
        text_block(img, ["「店内ですか？", "お持ち帰りですか？」"], W / 2, 420, 64, NAVY)
        n = 3 - int(t - 2.2)
        frac = (t - 2.2) % 1.0
        r = 210
        cx, cy = W / 2, 980
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=NAVY, width=6)
        d.arc([cx - r, cy - r, cx + r, cy + r], start=-90, end=-90 + 360 * frac, fill=ORA, width=22)
        f = font(int(230 * (1.15 - 0.15 * ease_out(frac * 3))))
        w = d.textlength(str(n), font=f)
        d.text((cx - w / 2, cy - 140), str(n), font=f, fill=NAVY, stroke_width=4, stroke_fill=NAVY)
        text_block(img, ["頭の中で言ってみて"], W / 2, 1290, 58, RED)
    elif t < 8.4:
        # ANSWER
        text_block(img, ["答え"], W / 2, 400, 60, RED)
        s = pop(t, 5.2, 0.3)
        text_block(img, ["Have here", "or takeaway?"], W / 2, 520, 120, NAVY, scale=s, highlight=YEL, gap=1.35)
        text_block(img, ["（店内ですか？お持ち帰りですか？）"], W / 2, 900, 46, ORA, scale=pop(t, 5.6))
        s2 = pop(t, 6.6)
        if s2:
            card(d, [140, 1060, 940, 1330])
            text_block(img, ["お客さん：", "Takeaway, thanks!"], W / 2, 1100, 66, NAVY, scale=s2)
    elif t < 10.8:
        # POINT
        f = font(44)
        d.rounded_rectangle([80, 380, 290, 460], radius=40, fill=ORA)
        d.text((112, 390), "POINT", font=f, fill=WHITE, stroke_width=1, stroke_fill=WHITE)
        text_block(img, ["to go より", "takeaway"], W / 2, 520, 104, NAVY, scale=pop(t, 8.4), gap=1.3)
        text_block(img, ["オーストラリアの現場で", "毎日聞くのはこっち"], W / 2, 830, 54, NAVY, scale=pop(t, 8.8), bold=False)
        s = pop(t, 9.3)
        if s:
            card(d, [110, 1040, 970, 1420])
            text_block(img, ["返事はこの3つでOK", "Have here, please.", "Dine in.", "Takeaway, thanks."], W / 2, 1075, 58, NAVY, scale=s, gap=1.4)
    else:
        # CTA: save + send drive reach
        text_block(img, ["明日のシフトで", "使えるように"], W / 2, 560, 84, NAVY, scale=pop(t, 10.8))
        text_block(img, ["保存しておいてね"], W / 2, 820, 96, ORA, scale=pop(t, 11.1), highlight=YEL)
        text_block(img, ["ワーホリ仲間にも送ってあげて"], W / 2, 1050, 54, NAVY, scale=pop(t, 11.4), bold=False)
    # shift content down so it sits in the middle of the Reels safe area
    body = img.crop((0, 300, W, H - 140))
    img.paste(Image.new("RGB", (W, H - 300), BG), (0, 300))
    img.paste(body, (0, 440))
    return img

def main():
    n = int(DUR * FPS)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", sys.argv[2],
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT,
    ], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    frame(1.6).save(OUT.replace(".mp4", "_cover.png"))
    for ts in (1.6, 3.5, 7.5, 10.0, 11.8):
        frame(ts).save(f"{sys.argv[3]}/check_{ts}.png")

main()
