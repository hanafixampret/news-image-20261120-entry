#!/usr/bin/env python3
"""Draw the front page of Friday 20 November 2026's world news as one image.

A 1024x1024 newspaper front page: a masthead, one lead story with a drawn
scene, nine story cards in three rows (the first row illustrated), and an
"ALSO TODAY" strip of ten more one-line stories -- twenty stories in all.

Everything is drawn with PIL primitives: no external images, no network,
no timestamps, no randomness. Running this file twice writes byte-identical
PNGs. Run:  python3 draw_news.py   (writes entry.png next to this file)
"""

import math
import os
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"

PAPER = (246, 241, 229)
INK = (18, 18, 18)
NAVY = (20, 38, 77)
NAVY_DK = (13, 25, 52)
GOLD = (233, 196, 88)
RED = (178, 34, 34)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
SKY = (168, 200, 228)


# ------------------------------------------------------------------ stories

@dataclass
class Story:
    kicker: str
    headline: str
    body: str
    art: str = ""  # "" = text only; otherwise the art-scene key


LEAD_KICKER = "LEAD  •  PEACE DECLARATION  •  SHENZHEN"
LEAD_HEADLINE = "TRUMP, XI & PUTIN SIGN 'PEACE DECLARATION'"
LEAD_BODY = (
    "First-ever trilateral summit ends with a four-point declaration on "
    "nuclear-risk talks, UN reform and oil supply -- but no deal on "
    "Ukraine, Iran or arms cuts."
)
LEAD_DATELINE = "Shenzhen  •  20 Nov 2026  —  US-China trade truce extended"

CARDS = [
    Story("ASIA  •  WEATHER",
          "CYCLONE AKVAN MAKES LANDFALL",
          "Severe storm hits the Odisha-Andhra coast; evacuations under "
          "way and schools shut.", "cyclone"),
    Story("MIDDLE EAST  •  GULF",
          "HOUTHI MISSILE HITS RIYADH TOWER",
          "Riyadh's tallest tower, the PIF Tower, damaged; windows "
          "blown out on seven floors.", "tower"),
    Story("EUROPE  •  WAR",
          "RUSSIAN STRIKES HIT KYIV EMBASSIES",
          "Austrian and Dutch embassies damaged in Kyiv; Ukraine hit the "
          "Crimean Bridge.", "kyiv"),
    Story("MIDDLE EAST  •  IRAN",
          "TRUMP WEIGHS NEW IRAN STRIKES",
          "Netanyahu pushes a 4-7 day air campaign; Gulf states urge "
          "restraint."),
    Story("MIDDLE EAST  •  IRAN",
          "IRAN STILL HOLDS 2,500 MISSILES",
          "US intelligence contradicts the claim its arsenal was "
          "destroyed."),
    Story("ASIA  •  JUSTICE",
          "ICJ: MYANMAR 'LIKELY' SOUGHT TO DESTROY ROHINGYA",
          "Court rules on the 2017 crackdown against the Rohingya "
          "minority."),
    Story("ASIA  •  KOREA",
          "SEOUL COURT CLEARS EX-PM HAN",
          "Supreme Court overturns Han Duck-soo's conviction over the "
          "2024 martial law."),
    Story("ASIA  •  CLIMATE",
          "FIJI DECLARES DROUGHT DISASTER",
          "El Nino drought leaves water shortages across the islands."),
    Story("TECH  •  CHIPS",
          "THE FALL OF JENSEN HUANG",
          "Nvidia chief's affair with Alice Huang drew US intelligence "
          "questions."),
]

ALSO_TODAY = [
    "VOYAGER 1 REACHES ONE LIGHT-DAY, NASA confirms",
    "US-VENEZUELA SIGN DEAL to restore military ties",
    "NORTH KOREA EXPANDING enrichment at Yongbyon",
    "MODI MEETS PRINCE AND PRINCESS OF WALES",
    "FIRE AT MUHAMMAD YUNUS ancestral home",
    "INDIA vs NZ: Nicholls 113* on day one",
    "SENSEX JUMPS 1.2% as Nifty tops 25,400",
    "GTA VI: day two in Vice City",
    "ANTHROPIC VALUATION reportedly $1.5 trillion",
    "EU PROPOSES \u20ac45BN Ukraine loan",
]


# ------------------------------------------------------------------ helpers

def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning the lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt_path, size, max_w, max_lines):
    """Shrink the font until the wrapped text fits in max_lines lines."""
    while size > 10:
        fnt = font(fnt_path, size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 2
    fnt = font(fnt_path, size)
    return fnt, wrap(draw, text, fnt, max_w)


def text_block(draw, x, y, lines, fnt, fill, leading):
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def panel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2,
                   fill=WHITE)


def gradient(draw, x, y, w, h, top, bottom):
    """Vertical colour gradient, one rectangle per row."""
    for i in range(h):
        t = i / max(1, h - 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        draw.rectangle([x, y + i, x + w, y + i + 1], fill=col)


def lit_windows(draw, x0, y0, bw, bh, lit=(252, 214, 110)):
    """Lit windows on one dark building."""
    cols = max(1, (bw - 8) // 11)
    rows = max(1, (bh - 10) // 13)
    for c in range(cols):
        for r in range(rows):
            if (c * 3 + r * 7) % 5 != 0:
                draw.rectangle(
                    [x0 + 5 + c * 11, y0 + 6 + r * 13,
                     x0 + 11 + c * 11, y0 + 12 + r * 13], fill=lit)


def skyline(draw, x0, y_base, x1, heights, color=(24, 32, 66)):
    """Row of dark buildings with lit windows, baseline y_base."""
    n = len(heights)
    bw = (x1 - x0) // n
    for i, hgt in enumerate(heights):
        bx = x0 + i * bw
        draw.rectangle([bx + 1, y_base - hgt, bx + bw - 2, y_base], fill=color)
        lit_windows(draw, bx + 1, y_base - hgt, bw, hgt)


def burst(draw, cx, cy, r_long, r_short, color, width=4):
    """Starburst: alternating long/short rays from a centre."""
    for ang in range(0, 360, 30):
        r = r_long if ang % 60 == 0 else r_short
        ex = cx + r * math.cos(math.radians(ang))
        ey = cy + r * math.sin(math.radians(ang))
        draw.line([cx, cy, ex, ey], fill=color, width=width)
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 200, 80))


def flag_us(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(178, 34, 34))
    for i in range(1, 7, 2):
        draw.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7],
                       fill=WHITE)
    draw.rectangle([x, y, x + w * 2 // 5, y + h * 4 // 7], fill=(30, 50, 110))
    for r in range(4):
        for c in range(5):
            draw.ellipse([x + 4 + c * 8, y + 3 + r * 7,
                          x + 7 + c * 8, y + 6 + r * 7], fill=WHITE)


def flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w // 5, y + h // 4
    draw.regular_polygon((cx, cy, 8), 5, rotation=-90, fill=GOLD)
    for dx, dy in ((22, 2), (26, 10), (22, 18), (14, 20)):
        draw.regular_polygon((x + dx, y + dy, 4), 5, rotation=-90, fill=GOLD)


def flag_ru(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=WHITE)
    draw.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(0, 57, 166))
    draw.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(213, 0, 50))


# ---------------------------------------------------------------- art scenes

def art_summit(d, x, y, w, h):
    """Dusk over Shenzhen: skyline, low sun, the three flags."""
    gradient(d, x, y, w, h, (24, 32, 66), (150, 92, 96))
    d.ellipse([x + w - 95, y + 16, x + w - 25, y + 86], fill=GOLD)
    skyline(d, x, y + h - 52, x + w, [150, 110, 190, 130, 170, 100, 150, 120])
    d.rectangle([x, y + h - 52, x + w, y + h], fill=(16, 20, 40))
    fw, fh = 84, 50
    fy = y + h - 46
    flag_us(d, x + 18, fy, fw, fh)
    flag_cn(d, x + 118, fy, fw, fh)
    flag_ru(d, x + 218, fy, fw, fh)
    d.text((x + 322, fy + 10), "APEC 2026", font=font(SANS_B, 24),
           fill=WHITE)


def art_cyclone(d, x, y, w, h):
    """Cyclone spiral over a stormy sea, rain slanting in."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(28, 90, 150))
    cx, cy = x + w // 2, y + h // 2 - 2
    rmax = min(24, h // 2 - 4)
    for r, col in ((rmax, (240, 240, 240)), (rmax - 7, (210, 225, 240)),
                   (rmax - 14, (170, 195, 220)), (7, (120, 160, 200))):
        if r > 3:
            d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col,
                  width=4)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(60, 90, 140))
    for rx in range(16, w, 30):
        d.line([x + rx, y + 6, x + rx - 5, y + 16], fill=(120, 150, 190),
               width=2)
    d.text((x + 10, y + h - 13), "EAST COAST \u2022 INDIA",
           font=font(SANS_B, 12), fill=WHITE)


def art_tower(d, x, y, w, h):
    """Riyadh at night: the PIF Tower with a blast at its crown."""
    d.rectangle([x, y, x + w, y + h], fill=(10, 14, 34))
    for sx, sy in ((22, 14), (70, 26), (250, 12), (300, 30), (140, 10)):
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
    tx = x + w // 2 - 28
    d.rectangle([tx, y + 24, tx + 56, y + h], fill=(74, 88, 124))
    for r in range(28, h - 4, 11):
        for c in range(4):
            if (r // 11 + c) % 3:
                d.rectangle([tx + 6 + c * 12, y + r, tx + 12 + c * 12,
                             y + r + 5], fill=(252, 214, 110))
    burst(d, x + w // 2, y + 20, 22, 12, (255, 140, 40))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(70, 55, 35))
    d.text((x + 10, y + h - 13), "RIYADH \u2022 KAFD",
           font=font(SANS_B, 12), fill=WHITE)


def art_kyiv(d, x, y, w, h):
    """Kyiv under fire: embassy facades, smoke and a blast."""
    gradient(d, x, y, w, h, (60, 70, 96), (140, 120, 100))
    bx = x + 30
    d.rectangle([bx, y + 26, bx + 150, y + h - 8], fill=(210, 198, 170))
    for i in range(4):
        d.rectangle([bx + 10 + i * 36, y + 36, bx + 32 + i * 36, y + 52],
                    fill=(40, 50, 70))
    d.rectangle([bx, y + 56, bx + 150, y + 60], fill=(120, 100, 70))
    d.polygon([(bx - 8, y + 26), (bx + 75, y + 8), (bx + 158, y + 26)],
              fill=(150, 40, 40))
    d.rectangle([x + w - 96, y + 34, x + w - 26, y + h - 8],
                fill=(188, 176, 148))
    for i in range(2):
        d.rectangle([x + w - 86 + i * 30, y + 42, x + w - 68 + i * 30,
                     y + 54], fill=(40, 50, 70))
    burst(d, x + w - 46, y + 22, 20, 11, (255, 140, 40))
    d.text((x + 10, y + 6), "KYIV", font=font(SANS_B, 12), fill=WHITE)


ART = {
    "cyclone": art_cyclone,
    "tower": art_tower,
    "kyiv": art_kyiv,
}


# ------------------------------------------------------------------- layout

def card_text(draw, x, y, w, story, head_size=19, body_size=14,
              head_lines=2, body_lines=2):
    """Kicker + headline + body inside a card starting at (x, y)."""
    draw.text((x, y), story.kicker, font=font(SANS_B, 13), fill=RED)
    y += 19
    hf, hlines = fit_lines(draw, story.headline, SERIF_B, head_size, w,
                           head_lines)
    y = text_block(draw, x, y, hlines, hf, INK, head_size + 4)
    y += 2
    bf = font(SANS, body_size)
    blines = wrap(draw, story.body, bf, w)[:body_lines]
    text_block(draw, x, y, blines, bf, (40, 40, 40), body_size + 4)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=3)

    # Masthead.
    d.rectangle([14, 14, W - 15, 110], fill=NAVY)
    d.text((W // 2, 24), "THE WORLD IN ONE IMAGE",
           font=font(SERIF_B, 54), fill=WHITE, anchor="ma")
    d.text((W // 2, 84), "FRIDAY  \u2022  20 NOVEMBER 2026  \u2022  WORLD NEWS",
           font=font(SANS_B, 22), fill=GOLD, anchor="ma")

    # Lead story: drawn scene left, text right.
    panel(d, 14, 118, 996, 232)
    art_summit(d, 16, 120, 462, 228)
    tx = 494
    d.text((tx, 130), LEAD_KICKER, font=font(SANS_B, 17), fill=RED)
    hf, hlines = fit_lines(d, LEAD_HEADLINE, SERIF_B, 40, 500, 2)
    y = text_block(d, tx, 156, hlines, hf, INK, 42)
    bf = font(SANS, 19)
    y = text_block(d, tx, y + 6, wrap(d, LEAD_BODY, bf, 500), bf,
                   (40, 40, 40), 25)
    d.text((tx, y + 6), LEAD_DATELINE, font=font(SANS_B, 16), fill=GREY)

    # Three rows of three story cards.
    cols = [14, 347, 680]
    rows = [(358, 164), (530, 146), (684, 146)]
    for row_i, (ry, rh) in enumerate(rows):
        for col_i, cx in enumerate(cols):
            story = CARDS[row_i * 3 + col_i]
            panel(d, cx, ry, 330, rh)
            if story.art:
                ART[story.art](d, cx + 2, ry + 2, 326, 54)
                card_text(d, cx + 12, ry + 62, 306, story,
                          head_size=18, body_size=13, body_lines=2)
            else:
                card_text(d, cx + 12, ry + 12, 306, story)

    # "Also today" strip: ten more one-line stories, two columns.
    panel(d, 14, 838, 996, 134)
    d.text((26, 848), "ALSO TODAY", font=font(SANS_B, 15), fill=RED)
    col_x = [26, 512]
    for i, line in enumerate(ALSO_TODAY):
        cx = col_x[i // 5]
        cy = 872 + (i % 5) * 20
        d.text((cx, cy), "\u2022  " + line, font=font(SANS, 14), fill=INK)

    d.text((W // 2, 984),
           "20 stories reported on Friday 20 November 2026.",
           font=font(SANS_I, 15), fill=GREY, anchor="ma")

    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
