#!/usr/bin/env python3
"""Draw the front page of Friday 20 November 2026's world news as one image.

A 1024x1024 newspaper front page, rebuilt to the format the leaderboard's
top entries share: a masthead naming the day, a strip of the day's big
numbers, a region count, three illustrated lead stories, ten feature cards,
a world map of where it happened, 23 more one-line stories, and a DATE
CHECK strip that names the previous day's news this page leaves out --
36 stories in all, every one of them first reported on Friday 20 November
2026, with its source.

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
MAPSEA = (16, 24, 52)
MAPLAND = (216, 206, 180)


# ------------------------------------------------------------------ stories

@dataclass
class Story:
    num: str
    place: str
    beat: str
    headline: str
    body: str
    source: str
    art: str = ""


LEADS = [
    Story("01", "ODISHA, INDIA", "CYCLONE",
          "Cyclone Akvan makes landfall in eastern India",
          "Severe storm crosses near Gopalpur; 300,000+ evacuated, winds "
          "gusting 110 km/h, 423 rescue teams deployed, schools shut.",
          "IMD, The Hindu", "cyclone"),
    Story("02", "KYIV, UKRAINE", "WAR",
          "Russia fires ~30 ballistic missiles at Kyiv",
          "Seven overnight waves hit energy and transport sites; fires "
          "burn in three districts; Dutch and Austrian embassies damaged.",
          "Kyiv Post, Reuters", "kyiv"),
    Story("03", "ANTALYA, TURKIYE", "CLIMATE",
          "COP31 reaches its final day deadlocked",
          "Closing draft omits fossil-fuel phase-out; $120bn adaptation "
          "finance unresolved; hosts push '35 by 35' clean-power goal.",
          "UN News, Reuters", "cop31"),
]

FEATURES = [
    Story("04", "SEOUL / TOKYO", "MARKETS",
          "AI sell-off sinks Asian markets",
          "Nikkei -4.5%, KOSPI -4.7%, SoftBank -16%; MSCI Asia-Pacific "
          "down 7%.",
          "Reuters", "chart"),
    Story("05", "MERCURY", "SPACE",
          "BepiColombo reaches Mercury",
          "ESA/JAXA probe ends 6bn-mile trip; orbit insertion set for "
          "Saturday.",
          "ESA, BBC", "mercury"),
    Story("06", "BRUSSELS", "EUROPE",
          "Burnham holds first EU-UK reset summit",
          "Costa and von der Leyen host UK PM; agrifood and carbon-market "
          "links eyed.",
          "EU Council", "reset"),
    Story("07", "TOKYO", "ECONOMY",
          "Japan inflation hits 2.3%",
          "Oct headline CPI rises from 2.1%; core stays above 2% for a "
          "second month.",
          "Reuters", "cpi"),
    Story("08", "BEIJING", "RATES",
          "China holds lending rates",
          "1-year LPR stays at 3.0%, 5-year at 3.5% as expected.",
          "PBOC, Reuters", "rates"),
    Story("09", "WELLINGTON", "CRICKET",
          "Phillips makes history: 118 vs India",
          "First NZ batter with centuries in all 3 formats vs India in a "
          "year. NZ 368.",
          "ICC, AP", "cricket"),
    Story("10", "SAN SALVADOR", "POLITICS",
          "Bukele registers for third term",
          "Files with electoral tribunal for Feb 2027 vote; rights groups "
          "object.",
          "AP", "ballot"),
    Story("11", "SENEGAL", "MIGRATION",
          "Migrant boat capsizes off Senegal",
          "Four dead; dozens missing from ~50-100 aboard as Canary "
          "arrivals surge.",
          "Al Jazeera", "boat"),
    Story("12", "ROME", "LABOUR",
          "Italy's CGIL holds 24-hr strike",
          "Unions rally in ~100 squares against 2027 budget; transit hit.",
          "CGIL, AFP", "strike"),
    Story("13", "BARCELONA", "HEALTH",
          "Cancer pill shrinks tumours 60.7%",
          "Daraxonrasib + chemo beats chemo alone (23-42%) in early trial.",
          "Reuters", "pill"),
]

# 23 more one-line stories: (number, place, text) -- kept under ~52 chars
# so each fits one line in its column.
ALSO_TODAY = [
    ("14", "BRAZIL", "Lula meets chief Raoni; land recognised"),
    ("15", "SEOUL", "Ruling party moves to impeach top judge"),
    ("16", "BOUGAINVILLE", "Rio Tinto pledges $370m for Panguna"),
    ("17", "CANBERRA", "AUKUS sub sales could shrink US fleet"),
    ("18", "FLORIDA", "St. Johns River hits record 18.3 ft"),
    ("19", "IOWA", "Army to detonate 68 unstable barrels"),
    ("20", "TONGA", "Emergency as El Nino drought bites"),
    ("21", "WASHINGTON", "US war cost vs Iran put at $48.3bn"),
    ("22", "LONDON", "UK & Norway fund 100m+ for naval vessels"),
    ("23", "COPENHAGEN", "Denmark approves Greenland defence bill"),
    ("24", "JAKARTA", "Indonesia passes asset-forfeiture bill"),
    ("25", "GLOBAL", "UN marks World Children's Day"),
    ("26", "CINCINNATI", "Zoo hippo Fiona dies after eating hat"),
    ("27", "SENEGAL", "Faye enacts budget by decree"),
    ("28", "HORMUZ", "Four attacks on vessels in 96 hours"),
    ("29", "NEW DELHI", "Pakistan minister to lead SCO dialogue"),
    ("30", "QATAR", "U17 World Cup: Australia stun Argentina 2-0"),
    ("31", "SOUTH AFRICA", "Proteas win Test; Bavuma sets record"),
    ("32", "HONG KONG", "Badminton Open reaches semifinals"),
    ("33", "TAIWAN", "Short-sell curbs in; bombers tracked"),
    ("34", "TURIN", "ATP Finals groups close; Alcaraz through"),
    ("35", "LOS ANGELES", "Thomas Markle fit to stand trial"),
    ("36", "WELLINGTON", "Nicholls 175* in 216-run stand"),
]

STATS = [
    ("300,000+", "evacuated - Cyclone Akvan"),
    ("~30", "ballistic missiles - Kyiv"),
    ("-7%", "Asia's worst week since 2020"),
    ("2.3%", "Japan Oct CPI - BoJ hike eyed"),
    ("118", "Phillips' century vs India"),
    ("8 yrs", "BepiColombo reaches Mercury"),
]

REGIONS = ("EUROPE 7  -  AMERICAS 8  -  ASIA-PACIFIC 10  -  MIDEAST 3  -  "
           "AFRICA 3  -  OCEANIA 4  -  WORLD 1")

DATE_CHECK = (
    "DATE CHECK - First reported Thursday 19 Nov, so NOT shown as Friday's "
    "news: the Trump-Xi-Putin Shenzhen summit - Anthropic's $83 IPO pricing "
    "& Nasdaq debut - the ICJ Myanmar Rohingya verdict - the GTA VI midnight "
    "launch - the $190.4m Van Gogh sale - Voyager 1's one light-day "
    "confirmation - the Senate's 48-51 Iran war-powers vote."
)

FOOTER = ("Every story here happened, or was first reported, on Friday "
          "20 November 2026. Claims are attributed, not stated as fact.")


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


def burst(draw, cx, cy, r_long, r_short, color, width=3):
    """Starburst: alternating long/short rays from a centre."""
    for ang in range(0, 360, 30):
        r = r_long if ang % 60 == 0 else r_short
        ex = cx + r * math.cos(math.radians(ang))
        ey = cy + r * math.sin(math.radians(ang))
        draw.line([cx, cy, ex, ey], fill=color, width=width)
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 200, 80))


# ---------------------------------------------------------------- art scenes

def art_cyclone(d, x, y, w, h):
    """Cyclone spiral over the Bay of Bengal, coast at the left."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(28, 90, 150))
    d.polygon([(x, y), (x + 78, y), (x + 62, y + h - 12), (x, y + h - 12)],
              fill=(214, 196, 150))
    cx, cy = x + w - 78, y + h // 2
    for r, col in ((30, (240, 240, 240)), (23, (210, 225, 240)),
                   (16, (170, 195, 220)), (9, (120, 160, 200))):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=4)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(60, 90, 140))
    for rx in range(90, w, 26):
        d.line([x + rx, y + 5, x + rx - 5, y + 14], fill=(120, 150, 190),
               width=2)
    d.text((x + 6, y + h - 11), "BAY OF BENGAL - LANDFALL 110 KM/H",
           font=font(SANS_B, 10), fill=WHITE)


def art_kyiv(d, x, y, w, h):
    """Night sky over Kyiv: missile trails over a dark skyline."""
    gradient(d, x, y, w, h, (14, 18, 44), (70, 60, 80))
    for sx, sy in ((30, 10), (90, 18), (180, 8), (260, 14), (300, 22)):
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
    for tx in (40, 130, 220, 290):
        d.line([x + tx, y + 6, x + tx + 34, y + 30], fill=(255, 140, 40),
               width=3)
        d.ellipse([x + tx + 32, y + 28, x + tx + 38, y + 34],
                  fill=(255, 200, 80))
    base = y + h
    for bx, bh in ((0, 26), (52, 40), (104, 30), (156, 46), (208, 34),
                   (260, 42), (306, 28)):
        d.rectangle([x + bx + 2, base - bh, x + bx + 22, base],
                    fill=(24, 28, 52))
        for wy in range(base - bh + 5, base - 4, 9):
            d.rectangle([x + bx + 6, wy, x + bx + 10, wy + 4],
                        fill=(252, 214, 110))
    d.text((x + 6, y + h - 11), "01:25 LOCAL - 7 WAVES",
           font=font(SANS_B, 10), fill=WHITE)


def art_cop31(d, x, y, w, h):
    """Globe and thermometer: a climate summit running hot."""
    d.rectangle([x, y, x + w, y + h], fill=(12, 44, 66))
    cx, cy = x + 62, y + h // 2
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(60, 140, 170))
    d.ellipse([cx - 26, cy - 20, cx - 2, cy + 4], fill=(90, 170, 120))
    d.ellipse([cx + 6, cy + 8, cx + 26, cy + 28], fill=(90, 170, 120))
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], outline=WHITE, width=2)
    tx = x + w - 62
    d.rounded_rectangle([tx, y + 8, tx + 16, y + h - 16], radius=8,
                        fill=WHITE)
    d.rectangle([tx + 3, y + h - 26, tx + 13, y + h - 12],
                fill=(178, 34, 34))
    d.ellipse([tx - 3, y + h - 22, tx + 19, y + h - 2], fill=(178, 34, 34))
    d.text((x + w - 96, y + 6), "COP31", font=font(SERIF_B, 22),
           fill=GOLD)
    d.text((x + 6, y + h - 11), "ANTALYA - FINAL DAY",
           font=font(SANS_B, 10), fill=WHITE)


def art_chart(d, x, y, w, h):
    """A market chart falling off a cliff."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 16, 20))
    pts = [(x + 6, y + 8), (x + 40, y + 14), (x + 74, y + 12),
           (x + 108, y + 22), (x + 142, y + 30), (x + 176, y + h - 8)]
    d.line(pts, fill=(220, 60, 60), width=3)
    d.line([x + 6, y + h - 8, x + w - 6, y + h - 8], fill=(90, 90, 90),
           width=1)
    d.text((x + w - 76, y + 4), "ASIA -7% WK", font=font(SANS_B, 11),
           fill=(255, 120, 120))


def art_mercury(d, x, y, w, h):
    """A probe closing on a cratered grey world."""
    d.rectangle([x, y, x + w, y + h], fill=(10, 12, 26))
    for sx, sy in ((16, 8), (60, 16), (120, 6), (170, 12)):
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
    cx, cy = x + w - 52, y + h // 2 + 4
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(150, 150, 150))
    for ox, oy, orr in ((-10, -6, 4), (6, 8, 5), (10, -10, 3)):
        d.ellipse([cx + ox - orr, cy + oy - orr, cx + ox + orr,
                   cy + oy + orr], fill=(110, 110, 110))
    d.line([x + 14, y + h - 12, cx - 22, cy - 2], fill=GOLD, width=2)
    d.polygon([(x + 8, y + h - 16), (x + 20, y + h - 16), (x + 14, y + h - 6)],
              fill=GOLD)
    d.text((x + 6, y + 4), "6BN MILES", font=font(SANS_B, 11),
           fill=(200, 200, 200))


def art_reset(d, x, y, w, h):
    """EU stars beside a Union Jack: the reset talks."""
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    cx, cy = x + 44, y + h // 2
    for k in range(12):
        ang = math.radians(k * 30 - 90)
        sx, sy = cx + 26 * math.cos(ang), cy + 16 * math.sin(ang)
        d.regular_polygon((sx, sy, 4), 5, rotation=-90, fill=GOLD)
    ux, uy = x + w - 88, y + 6
    d.rectangle([ux, uy, ux + 76, uy + h - 12], fill=(200, 16, 46))
    d.line([ux, uy, ux + 76, uy + h - 12], fill=WHITE, width=6)
    d.line([ux + 76, uy, ux, uy + h - 12], fill=WHITE, width=6)
    d.line([ux + 38, uy, ux + 38, uy + h - 12], fill=WHITE, width=10)
    d.line([ux, uy + (h - 12) // 2, ux + 76, uy + (h - 12) // 2],
           fill=WHITE, width=10)
    d.text((x + 6, y + 4), "RESET TALKS", font=font(SANS_B, 11),
           fill=WHITE)


def art_cpi(d, x, y, w, h):
    """Two bars: CPI 2.1% last month, 2.3% now, over a 2% line."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 236, 224))
    d.line([x + 8, y + 12, x + w - 8, y + 12], fill=RED, width=2)
    d.text((x + 8, y + 2), "2% TARGET", font=font(SANS_B, 9), fill=RED)
    d.rectangle([x + 34, y + 20, x + 74, y + h - 6], fill=(120, 120, 120))
    d.rectangle([x + 104, y + 14, x + 144, y + h - 6], fill=NAVY)
    d.text((x + 36, y + h - 16), "2.1%", font=font(SANS_B, 10), fill=WHITE)
    d.text((x + 106, y + h - 16), "2.3%", font=font(SANS_B, 10),
           fill=WHITE)


def art_rates(d, x, y, w, h):
    """Two rate cards: 3.00% for one year, 3.50% for five."""
    d.rectangle([x, y, x + w, y + h], fill=(20, 38, 77))
    d.rectangle([x + 10, y + 6, x + 88, y + h - 6], fill=WHITE)
    d.rectangle([x + 98, y + 6, x + w - 10, y + h - 6], fill=WHITE)
    d.text((x + 14, y + 8), "3.00%", font=font(SANS_B, 15), fill=NAVY)
    d.text((x + 18, y + 26), "1Y", font=font(SANS_B, 10), fill=GREY)
    d.text((x + 102, y + 8), "3.50%", font=font(SANS_B, 15), fill=NAVY)
    d.text((x + 106, y + 26), "5Y", font=font(SANS_B, 10), fill=GREY)


def art_cricket(d, x, y, w, h):
    """A bat, a red ball, and the hundred."""
    d.rectangle([x, y, x + w, y + h], fill=(34, 90, 50))
    d.line([x + 30, y + 6, x + 70, y + h - 10], fill=(220, 190, 130),
           width=8)
    d.ellipse([x + w - 52, y + 6, x + w - 26, y + 32], fill=(178, 34, 34),
              outline=WHITE, width=2)
    d.text((x + 6, y + 4), "118", font=font(SERIF_B, 22), fill=WHITE)
    d.text((x + 6, y + h - 14), "RECORD", font=font(SANS_B, 10),
           fill=GOLD)


def art_ballot(d, x, y, w, h):
    """A ballot box marked 2027."""
    d.rectangle([x, y, x + w, y + h], fill=(70, 60, 120))
    d.rectangle([x + 60, y + 10, x + w - 60, y + h - 8], fill=(240, 236, 224))
    d.rectangle([x + 74, y + 6, x + w - 74, y + 12], fill=INK)
    d.rectangle([x + 84, y + 2, x + 108, y + 12], fill=WHITE,
                outline=INK, width=2)
    d.text((x + 64, y + h - 16), "2027", font=font(SANS_B, 12), fill=WHITE)


def art_boat(d, x, y, w, h):
    """A small boat on a heavy sea off the coast."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(28, 90, 150))
    d.polygon([(x + 40, y + h - 20), (x + w - 40, y + h - 20),
               (x + w - 56, y + h - 8), (x + 56, y + h - 8)],
              fill=(120, 70, 40))
    d.line([x + w // 2, y + 6, x + w // 2, y + h - 20], fill=INK, width=2)
    d.polygon([(x + w // 2, y + 6), (x + w // 2 + 26, y + h - 22),
               (x + w // 2, y + h - 22)], fill=WHITE)
    d.text((x + 6, y + 4), "YENNE COAST", font=font(SANS_B, 10),
           fill=NAVY_DK)


def art_strike(d, x, y, w, h):
    """Green, white and red: a general strike."""
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    d.rectangle([x, y, x + w // 3, y + h], fill=(0, 140, 70))
    d.rectangle([x + 2 * w // 3, y, x + w, y + h], fill=(205, 40, 50))
    d.text((x + w // 2, y + h // 2 - 10), "24H", font=font(SANS_B, 18),
           fill=INK, anchor="ma")
    d.text((x + 6, y + 4), "SCIOPERO", font=font(SANS_B, 10), fill=INK)


def art_pill(d, x, y, w, h):
    """A capsule, half red, half white, over a chart line."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 236, 224))
    d.line([x + 8, y + h - 10, x + w - 8, y + 8], fill=(90, 140, 90),
           width=3)
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 52, cy - 12, cx + 52, cy + 12], fill=WHITE,
              outline=INK, width=2)
    d.pieslice([cx - 52, cy - 12, cx + 52, cy + 12], 270, 90,
               fill=(178, 34, 34))
    d.rectangle([cx - 2, cy - 12, cx + 2, cy + 12], fill=INK)
    d.text((x + 6, y + 4), "60.7%", font=font(SANS_B, 12), fill=RED)


ART = {
    "cyclone": art_cyclone,
    "kyiv": art_kyiv,
    "cop31": art_cop31,
    "chart": art_chart,
    "mercury": art_mercury,
    "reset": art_reset,
    "cpi": art_cpi,
    "rates": art_rates,
    "cricket": art_cricket,
    "ballot": art_ballot,
    "boat": art_boat,
    "strike": art_strike,
    "pill": art_pill,
}


# ------------------------------------------------------------------- layout

def lead_card(draw, x, y, w, h, story):
    panel(draw, x, y, w, h)
    ART[story.art](draw, x + 2, y + 2, w - 4, 64)
    ty = y + 72
    draw.text((x + 12, ty), "%s  -  %s  -  %s" % (
        story.num, story.place, story.beat),
        font=font(SANS_B, 12), fill=RED)
    ty += 18
    hf, hlines = fit_lines(draw, story.headline, SERIF_B, 20, w - 24, 2)
    ty = text_block(draw, x + 12, ty, hlines, hf, INK, 23)
    ty += 2
    bf = font(SANS, 13)
    body = story.body + " (" + story.source + ")"
    blines = wrap(draw, body, bf, w - 24)[:3]
    text_block(draw, x + 12, ty, blines, bf, (40, 40, 40), 17)


def feature_card(draw, x, y, w, h, story):
    panel(draw, x, y, w, h)
    ART[story.art](draw, x + 2, y + 2, w - 4, 44)
    ty = y + 50
    draw.text((x + 10, ty), "%s  -  %s" % (story.num, story.place),
              font=font(SANS_B, 11), fill=RED)
    draw.text((x + 10, ty + 13), story.beat, font=font(SANS_B, 10),
              fill=GREY)
    ty += 26
    hf, hlines = fit_lines(draw, story.headline, SERIF_B, 15, w - 20, 2)
    ty = text_block(draw, x + 10, ty, hlines, hf, INK, 17)
    bf = font(SANS, 11)
    body = story.body + " (" + story.source + ")"
    blines = wrap(draw, body, bf, w - 20)[:3]
    text_block(draw, x + 10, ty + 2, blines, bf, (40, 40, 40), 13)


# Simplified continent outlines for the "where it happened" map.
# Coordinates are inside the map box (298 x 176).
CONTINENTS = [
    [(10, 28), (55, 14), (92, 24), (88, 48), (62, 62), (38, 58), (16, 42)],
    [(72, 88), (98, 82), (108, 104), (92, 138), (76, 116)],
    [(148, 22), (172, 14), (186, 26), (176, 44), (156, 42)],
    [(152, 56), (182, 50), (196, 70), (182, 102), (162, 98), (148, 74)],
    [(192, 18), (252, 12), (288, 26), (284, 54), (244, 64), (216, 50),
     (196, 36)],
    [(258, 112), (286, 106), (292, 124), (264, 130)],
]

# (number, x, y) pins on the same map box.
PINS = [
    ("1", 250, 56), ("2", 176, 28), ("3", 182, 44), ("4", 282, 40),
    ("6", 158, 24), ("7", 286, 44), ("8", 266, 36), ("9", 290, 128),
    ("10", 48, 56), ("11", 146, 66), ("12", 166, 40), ("13", 152, 36),
]


def world_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=MAPSEA)
    for poly in CONTINENTS:
        draw.polygon([(x + px, y + py) for px, py in poly], fill=MAPLAND)
    for num, px, py in PINS:
        cx, cy = x + px, y + py
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                     outline=WHITE, width=1)
        draw.text((cx, cy - 4), num, font=font(SANS_B, 8), fill=WHITE,
                  anchor="ma")
    draw.text((x + 8, y + h - 16), "SPACE: Mercury (5)",
              font=font(SANS_B, 10), fill=GOLD)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=3)

    # Masthead.
    d.rectangle([14, 14, W - 15, 100], fill=NAVY)
    d.text((W // 2, 22), "THE WORLD IN ONE PAGE  -  36 STORIES  -  "
           "6 CONTINENTS", font=font(SANS_B, 15), fill=GOLD, anchor="ma")
    d.text((W // 2, 34), "Friday 20 November 2026",
           font=font(SERIF_B, 42), fill=WHITE, anchor="ma")
    d.text((W // 2, 84), "Cyclone Akvan strikes India  -  Missiles hit "
           "Kyiv  -  COP31 deadlocked  -  Asia sells off",
           font=font(SANS, 15), fill=GOLD, anchor="ma")

    # Stat strip: the day's big numbers.
    cell_w = 166
    for i, (num, label) in enumerate(STATS):
        cx = 14 + i * cell_w
        if i:
            d.line([cx, 108, cx, 148], fill=(200, 190, 170), width=1)
        d.text((cx + cell_w // 2, 110), num, font=font(SERIF_B, 24),
               fill=RED if i % 2 == 0 else NAVY, anchor="ma")
        d.text((cx + cell_w // 2, 138), label, font=font(SANS, 11),
               fill=GREY, anchor="ma")

    # Region bar.
    d.text((14, 156), REGIONS, font=font(SANS_B, 12), fill=NAVY)
    d.text((W - 14, 156), "ALL STORIES FRI 20 NOV 2026",
           font=font(SANS_B, 12), fill=GREY, anchor="ra")

    # Three lead stories.
    for i, story in enumerate(LEADS):
        lead_card(d, 14 + i * 333, 178, 330, 190, story)

    # Ten feature cards, two rows of five.
    for i, story in enumerate(FEATURES):
        col, row = i % 5, i // 5
        feature_card(d, 14 + col * 198, 376 + row * 164, 192, 156, story)

    # World map, left; also-today list, right.
    panel(d, 14, 704, 330, 242)
    d.text((26, 712), "WHERE IT HAPPENED", font=font(SANS_B, 14), fill=RED)
    world_map(d, 22, 734, 314, 176)
    d.text((26, 918), "Pins 1-3 Lead  -  Pins 4-13 Feature stories",
           font=font(SANS, 11), fill=GREY)

    panel(d, 352, 704, 658, 242)
    d.text((364, 712), "ALSO ON FRIDAY 20 NOVEMBER - 23 MORE STORIES",
           font=font(SANS_B, 14), fill=RED)
    col_x = [364, 688]
    for i, (num, place, text) in enumerate(ALSO_TODAY):
        cx = col_x[i // 12]
        cy = 736 + (i % 12) * 17
        d.text((cx, cy), num, font=font(SANS_B, 11), fill=RED)
        d.text((cx + 24, cy), "%s - %s" % (place, text),
               font=font(SANS, 11), fill=INK)

    # Date check: what this page leaves out, and why.
    dcf = font(SANS, 12)
    dc_lines = wrap(d, DATE_CHECK, dcf, 972)
    text_block(d, 26, 954, dc_lines, dcf, INK, 16)
    d.text((W // 2, 994), FOOTER, font=font(SANS_I, 12), fill=GREY,
           anchor="ma")

    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
