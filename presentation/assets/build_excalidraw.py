#!/usr/bin/env python3
"""
Generate an Excalidraw scene file describing the taxonomy application
architecture, in the same zoned-with-dashed-boundaries style as the
reference supplied for the oral.

Re-run this script when you want to regenerate the .excalidraw file:

    python3 presentation/assets/build_excalidraw.py

Then in Excalidraw (excalidraw.com) use File -> Open to load the .excalidraw
file, adjust visually if needed, and File -> Export -> PNG (with embedded
scene). Drop the PNG into presentation/assets/ and docs/.

Changes vs v1:
- Labels inside boxes are free-floating centered text, not container-bound,
  so the primary label actually shows up (v1 binding dropped the text).
- Long sub-labels are split over multiple lines to avoid truncation.
- Arrows that cross other boxes use elbowed waypoints instead of going
  diagonally through them.
- Arrow labels are bound to the arrow element (Excalidraw auto-centers
  them at the midpoint and they follow the arrow when you drag it).
- Tech logos (Next.js, Prisma, Postgres, GitHub, Stripe, Chrome) are
  fetched from gilbarbara/logos and embedded as base64 images inside
  each box. If the fetch fails the generator falls back to placeholder
  rectangles so the scene still opens.
"""

import base64
import itertools
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

OUTPUT = Path(__file__).parent / "architecture-taxonomy.excalidraw"
NOW_MS = int(time.time() * 1000)

_id_iter = itertools.count(1)
_seed_iter = itertools.count(10_000)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{next(_id_iter):03d}"


# ---------------------------------------------------------------------------
# Element factory boilerplate
# ---------------------------------------------------------------------------

def _base(id_: str) -> dict:
    return {
        "id": id_,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": next(_seed_iter),
        "version": 1,
        "versionNonce": next(_seed_iter),
        "isDeleted": False,
        "boundElements": [],
        "updated": NOW_MS,
        "link": None,
        "locked": False,
    }


def rect(prefix, x, y, w, h, fill=None, rounded=True, stroke="#1e1e1e"):
    el = _base(_new_id(prefix))
    el.update(
        type="rectangle",
        x=x, y=y, width=w, height=h,
        roundness={"type": 3} if rounded else None,
        strokeColor=stroke,
    )
    if fill:
        el.update(backgroundColor=fill, fillStyle="solid")
    return el


def _approx_text_width(content: str, size: int) -> int:
    """Conservative monospace-ish estimate (Virgil is wider than monospace)."""
    longest_line = max(content.split("\n"), key=len) if "\n" in content else content
    return max(40, int(size * 0.62 * len(longest_line)))


def _text_height(content: str, size: int) -> int:
    lines = content.count("\n") + 1
    return int(size * 1.35 * lines)


def text(prefix, x, y, content, size=20, color="#1e1e1e",
         align="center", w=None, h=None):
    if w is None:
        w = _approx_text_width(content, size)
    if h is None:
        h = _text_height(content, size)
    el = _base(_new_id(prefix))
    el.update(
        type="text",
        x=x, y=y, width=w, height=h,
        text=content,
        fontSize=size,
        fontFamily=1,  # 1 = Virgil (hand-drawn)
        textAlign=align,
        verticalAlign="middle",
        containerId=None,
        originalText=content,
        lineHeight=1.25,
        baseline=int(size * 0.85),
        strokeColor=color,
    )
    return el


def centered_text_in_box(prefix, box, content, size=22, color="#1e1e1e",
                         y_anchor="center", y_offset=0):
    """Drop a free-floating text element visually centered inside a box.

    y_anchor: 'center' (default), 'top' (aligned near top), 'bottom'.
    y_offset: extra pixels nudged from the anchor.
    """
    w = _approx_text_width(content, size)
    h = _text_height(content, size)
    cx = box["x"] + box["width"] / 2
    if y_anchor == "center":
        cy = box["y"] + box["height"] / 2
    elif y_anchor == "top":
        cy = box["y"] + h / 2 + 12
    elif y_anchor == "bottom":
        cy = box["y"] + box["height"] - h / 2 - 12
    else:
        cy = box["y"] + box["height"] / 2
    return text(prefix, int(cx - w / 2), int(cy - h / 2 + y_offset),
                content, size=size, color=color, w=w, h=h)


def line(prefix, x1, y1, x2, y2, dashed=False):
    el = _base(_new_id(prefix))
    el.update(
        type="line",
        x=x1, y=y1,
        width=abs(x2 - x1) or 1,
        height=abs(y2 - y1) or 1,
        points=[[0, 0], [x2 - x1, y2 - y1]],
        lastCommittedPoint=None,
        startBinding=None, endBinding=None,
        startArrowhead=None, endArrowhead=None,
        strokeStyle="dashed" if dashed else "solid",
    )
    return el


def arrow_from_points(prefix, anchor_xy, points_rel,
                      start_id=None, end_id=None,
                      start_focus=0, end_focus=0, gap=8,
                      color="#1e1e1e"):
    """Elbow-friendly arrow. 'points_rel' is a list of [dx, dy] relative to anchor."""
    x0, y0 = anchor_xy
    xs = [p[0] for p in points_rel]
    ys = [p[1] for p in points_rel]
    el = _base(_new_id(prefix))
    el.update(
        type="arrow",
        x=x0, y=y0,
        width=max(1, max(xs) - min(xs)),
        height=max(1, max(ys) - min(ys)),
        points=[list(p) for p in points_rel],
        lastCommittedPoint=None,
        startBinding=({"elementId": start_id, "focus": start_focus, "gap": gap}
                      if start_id else None),
        endBinding=({"elementId": end_id, "focus": end_focus, "gap": gap}
                    if end_id else None),
        startArrowhead=None,
        endArrowhead="arrow",
        strokeColor=color,
    )
    return el


def straight_arrow(prefix, x1, y1, x2, y2, **kwargs):
    return arrow_from_points(prefix, (x1, y1),
                             [[0, 0], [x2 - x1, y2 - y1]], **kwargs)


def elbow_arrow(prefix, x1, y1, x2, y2, mid_x=None, mid_y=None, **kwargs):
    """Horizontal-then-vertical-then-horizontal elbow."""
    pts = [[0, 0]]
    if mid_x is not None:
        pts.append([mid_x - x1, 0])
        pts.append([mid_x - x1, y2 - y1])
    elif mid_y is not None:
        pts.append([0, mid_y - y1])
        pts.append([x2 - x1, mid_y - y1])
    pts.append([x2 - x1, y2 - y1])
    return arrow_from_points(prefix, (x1, y1), pts, **kwargs)


# Image element support --------------------------------------------------

_files: dict[str, dict] = {}


def _add_file(data_uri: str, mime: str) -> str:
    fid = f"file-{len(_files):03d}"
    _files[fid] = {
        "mimeType": mime,
        "id": fid,
        "dataURL": data_uri,
        "created": NOW_MS,
        "lastRetrieved": NOW_MS,
    }
    return fid


def fetch_logo(url: str) -> tuple[str, str] | None:
    """Fetch a logo URL and return (data_uri, mime), or None on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "build-excalidraw"})
        with urllib.request.urlopen(req, timeout=8) as f:
            raw = f.read()
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"  !! fetch failed for {url}: {e}")
        return None
    mime = ("image/svg+xml" if url.endswith(".svg")
            else "image/png" if url.endswith(".png")
            else "image/jpeg")
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{encoded}", mime


def image(prefix, x, y, w, h, data_uri: str, mime: str):
    fid = _add_file(data_uri, mime)
    el = _base(_new_id(prefix))
    el.update(
        type="image",
        x=x, y=y, width=w, height=h,
        status="saved",
        fileId=fid,
        scale=[1, 1],
        strokeColor="transparent",
        backgroundColor="transparent",
        roughness=0,
        strokeWidth=1,
    )
    return el


# ---------------------------------------------------------------------------
# Scene composition
# ---------------------------------------------------------------------------

elements: list[dict] = []


def add(el):
    elements.append(el)
    return el


def add_arrow_with_label(arrow_el, label: str, label_size=14, color="#1e1e1e"):
    """Create an arrow and bind a label that Excalidraw auto-centers on it."""
    add(arrow_el)
    # Excalidraw auto-repositions text whose containerId is an arrow.
    lbl = text("albl", 0, 0, label, size=label_size, color=color)
    lbl["containerId"] = arrow_el["id"]
    arrow_el["boundElements"].append({"id": lbl["id"], "type": "text"})
    add(lbl)
    return arrow_el


# --- Try to fetch logos -------------------------------------------------
#
# gilbarbara/logos is a reliable static hosting of tech brand SVGs. If the
# host is unreachable the script still produces a diagram, only without the
# embedded icons.
LOGO_URLS = {
    "nextjs":     "https://raw.githubusercontent.com/gilbarbara/logos/main/logos/nextjs-icon.svg",
    "prisma":     "https://raw.githubusercontent.com/gilbarbara/logos/main/logos/prisma.svg",
    "postgresql": "https://raw.githubusercontent.com/gilbarbara/logos/main/logos/postgresql.svg",
    "github":     "https://raw.githubusercontent.com/gilbarbara/logos/main/logos/github-icon.svg",
    "stripe":     "https://raw.githubusercontent.com/gilbarbara/logos/main/logos/stripe.svg",
    "chrome":     "https://raw.githubusercontent.com/gilbarbara/logos/main/logos/chrome.svg",
    "mdx":        "https://raw.githubusercontent.com/gilbarbara/logos/main/logos/mdx.svg",
    "postmark":   "https://raw.githubusercontent.com/gilbarbara/logos/main/logos/postmark-icon.svg",
}

logo_assets: dict[str, tuple[str, str]] = {}
print("Fetching tech logos...")
for name, url in LOGO_URLS.items():
    got = fetch_logo(url)
    if got:
        logo_assets[name] = got
        print(f"  ok  {name}")
print(f"  {len(logo_assets)}/{len(LOGO_URLS)} logos embedded\n")


def logo_or_placeholder(prefix, x, y, w, h, name: str):
    """Return an image element if the logo was fetched, else a faint rect."""
    if name in logo_assets:
        data_uri, mime = logo_assets[name]
        return image(prefix, x, y, w, h, data_uri, mime)
    # Fallback placeholder: a dashed rect the user can replace with drag-drop.
    ph = rect(prefix + "-ph", x, y, w, h, fill="#f0f0f0", rounded=True,
              stroke="#bbbbbb")
    ph["strokeStyle"] = "dashed"
    return ph


# --- Canvas layout (~ 1650 x 900 visible area) -------------------------

# Title
add(text("title", 540, 24, "Architecture · taxonomy (Next.js 13)",
         size=30, w=720))

# Zone labels (red, bold-ish)
add(text("zlbl", 140, 96, "CLIENT", size=18, color="#a8341c", w=200))
add(text("zlbl", 520, 96, "APPLICATION", size=18, color="#a8341c", w=280))
add(text("zlbl", 900, 96, "DONNÉES", size=18, color="#a8341c", w=240))
add(text("zlbl", 1280, 96, "SERVICES EXTERNES", size=18, color="#a8341c", w=320))

# Boundary captions
add(text("bcap", 360, 132, "(Browser ↔ Server)", size=12, color="#888", w=220))
add(text("bcap", 760, 132, "(Server ↔ DB)", size=12, color="#888", w=180))
add(text("bcap", 1140, 132, "(Internal ↔ External)", size=12, color="#888", w=240))

# Boundary dashed lines
add(line("bnd", 420, 160, 420, 820, dashed=True))
add(line("bnd", 820, 160, 820, 820, dashed=True))
add(line("bnd", 1200, 160, 1200, 820, dashed=True))


# --- CLIENT zone --------------------------------------------------------

user_box = add(rect("user", 140, 380, 240, 170, fill="#fff8e6"))
add(logo_or_placeholder("user-logo", 160, 395, 50, 50, "chrome"))
add(centered_text_in_box("user-lbl", user_box, "Navigateur",
                         size=22, y_anchor="center", y_offset=10))
add(centered_text_in_box("user-sub", user_box,
                         "Chrome · Safari · Firefox",
                         size=13, color="#555", y_anchor="bottom"))


# --- APPLICATION zone ---------------------------------------------------

# Contentlayer (build-time, top)
ctl_box = add(rect("ctl", 460, 210, 320, 80, fill="#f4ecff"))
add(logo_or_placeholder("ctl-logo", 478, 225, 42, 42, "mdx"))
add(centered_text_in_box("ctl-lbl", ctl_box, "Contentlayer",
                         size=20, y_anchor="top"))
add(centered_text_in_box("ctl-sub", ctl_box, "MDX compilé au build",
                         size=13, color="#555", y_anchor="bottom"))

# Next.js main box
nx_box = add(rect("next", 460, 360, 320, 220, fill="#e6f0ff"))
add(logo_or_placeholder("next-logo", 480, 380, 54, 54, "nextjs"))
add(centered_text_in_box(
    "next-lbl", nx_box, "Next.js 13 · App Router",
    size=22, y_anchor="center", y_offset=-6,
))
add(centered_text_in_box(
    "next-sub", nx_box,
    "Server Components · API routes\nNextAuth · Prisma client",
    size=13, color="#555", y_anchor="bottom",
))


# --- DONNÉES zone -------------------------------------------------------
#
# Prisma and Postgres are stacked with a 60px gap centered at y=430 so that
# the Next.js -> Stripe arrow can pass through the gap as a clean straight
# horizontal line without crossing any box.

prisma_box = add(rect("prisma", 860, 300, 220, 100, fill="#e8fbf3"))
add(logo_or_placeholder("prisma-logo", 878, 318, 42, 42, "prisma"))
add(centered_text_in_box("prisma-lbl", prisma_box, "Prisma ORM",
                         size=20, y_anchor="center", y_offset=8))

pg_box = add(rect("pg", 860, 460, 220, 160, fill="#e8fbf3"))
add(logo_or_placeholder("pg-logo", 878, 478, 48, 48, "postgresql"))
add(centered_text_in_box("pg-lbl", pg_box, "PostgreSQL",
                         size=20, y_anchor="center", y_offset=-6))
add(centered_text_in_box("pg-sub", pg_box, "users · posts · subs",
                         size=13, color="#555", y_anchor="bottom"))


# --- SERVICES EXTERNES zone --------------------------------------------

gh_box = add(rect("gh", 1240, 220, 280, 110, fill="#f5f5f5"))
add(logo_or_placeholder("gh-logo", 1258, 240, 48, 48, "github"))
add(centered_text_in_box("gh-lbl", gh_box, "GitHub OAuth",
                         size=20, y_anchor="center", y_offset=8))

# Stripe is centered on y=430 to line up with the Prisma/Postgres gap,
# so the Next.js -> Stripe arrow stays axis-aligned.
stripe_box = add(rect("stripe", 1240, 375, 280, 110, fill="#f5f5f5"))
add(logo_or_placeholder("stripe-logo", 1258, 395, 48, 48, "stripe"))
add(centered_text_in_box("stripe-lbl", stripe_box, "Stripe",
                         size=20, y_anchor="center", y_offset=-8))
add(centered_text_in_box("stripe-sub", stripe_box,
                         "checkout · webhook",
                         size=13, color="#555", y_anchor="bottom"))

postmark_box = add(rect("postmark", 1240, 540, 280, 110, fill="#f5f5f5"))
add(logo_or_placeholder("postmark-logo", 1258, 560, 48, 48, "postmark"))
add(centered_text_in_box("post-lbl", postmark_box, "Postmark",
                         size=20, y_anchor="center", y_offset=-8))
add(centered_text_in_box("post-sub", postmark_box,
                         "emails transactionnels",
                         size=13, color="#555", y_anchor="bottom"))


# --- Arrows --------------------------------------------------------------
#
# Routing rules:
#   * Cross-zone arrows use elbow waypoints so they never pass through a
#     box that sits between source and target.
#   * "mid_y" elbow = vertical -> horizontal -> vertical. We use this for
#     GitHub (route above Prisma) and Postmark (route below Postgres).
#   * "mid_x" elbow = horizontal -> vertical -> horizontal. Not useful
#     here because the data column sits on every mid_x path.
#   * The Stripe arrow is a plain straight line in the 60px gap between
#     Prisma (bottom y=400) and Postgres (top y=460).

# user <-> Next.js
add_arrow_with_label(
    straight_arrow("a-req", 380, 430, 460, 430,
                   start_id=user_box["id"], end_id=nx_box["id"]),
    "HTTPs Request", label_size=13,
)
add_arrow_with_label(
    straight_arrow("a-res", 460, 520, 380, 520,
                   start_id=nx_box["id"], end_id=user_box["id"]),
    "HTML / RSC stream", label_size=13,
)

# Contentlayer -> Next.js (build-time, vertical)
add_arrow_with_label(
    straight_arrow("a-mdx", 620, 290, 620, 360,
                   start_id=ctl_box["id"], end_id=nx_box["id"]),
    "MDX (build)", label_size=12,
)

# Next.js -> Prisma (horizontal at Prisma vertical centre)
add_arrow_with_label(
    straight_arrow("a-orm", 780, 370, 860, 370,
                   start_id=nx_box["id"], end_id=prisma_box["id"]),
    "query / mutation", label_size=13,
)

# Prisma -> Postgres (vertical through the gap)
add_arrow_with_label(
    straight_arrow("a-sql", 970, 400, 970, 460,
                   start_id=prisma_box["id"], end_id=pg_box["id"]),
    "SQL", label_size=14,
)

# Next.js -> GitHub OAuth: go UP first (clears Prisma at y=300),
# then across above the data zone, then down into GitHub.
add_arrow_with_label(
    elbow_arrow("a-oauth", 780, 380, 1240, 275, mid_y=260,
                start_id=nx_box["id"], end_id=gh_box["id"]),
    "OAuth (NextAuth)", label_size=12,
)

# Next.js -> Stripe: straight horizontal through the Prisma/Postgres gap.
add_arrow_with_label(
    straight_arrow("a-stripe", 780, 430, 1240, 430,
                   start_id=nx_box["id"], end_id=stripe_box["id"]),
    "checkout · webhook", label_size=12,
)

# Next.js -> Postmark: go DOWN first (clears Postgres at y=620),
# then across below the data zone, then up into Postmark.
add_arrow_with_label(
    elbow_arrow("a-mail", 780, 560, 1240, 595, mid_y=650,
                start_id=nx_box["id"], end_id=postmark_box["id"]),
    "send email", label_size=12,
)


# --- Scene serialization -----------------------------------------------

scene = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": elements,
    "appState": {
        "viewBackgroundColor": "#fdfaf2",
        "currentItemFontFamily": 1,
        "gridSize": None,
    },
    "files": _files,
}

OUTPUT.write_text(json.dumps(scene, indent=2, ensure_ascii=False))
print(f"wrote {OUTPUT}")
print(f"  elements: {len(elements)}")
print(f"  embedded files: {len(_files)}")
print(f"  size: {OUTPUT.stat().st_size / 1024:.1f} KB")
