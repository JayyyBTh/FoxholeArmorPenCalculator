#!/usr/bin/env python3
"""
Measure progress-bar fill as a LENGTH fraction, from a screenshot.

Darkest colour  -> background
Middle colour   -> remaining
Lightest colour -> done

Samples a single profile down the bar's axis instead of counting area, and
locates the three boundaries by sub-pixel interpolation, so the soft edges
typical of screenshots don't bias the result.

Writes an annotated copy: green beside the done span, red beside remaining.
"""

import argparse
import numpy as np
from PIL import Image

# Baked-in profile values for --fast, ordered dark -> light.
DEFAULT_PALETTE = np.array([78.0, 131.0, 165.0])


def profile(gray, keep=0.6):
    """Median down the bar's core columns.

    Columns are chosen by how much they vary ALONG the bar, not by position.
    A core column swings the full mid->light contrast; a blurred edge column
    swings less, and a background column not at all. This works even when the
    crop is off-centre or the bar occupies only part of the width, which a
    fixed central band gets badly wrong.
    """
    if gray.shape[1] == 1:
        return gray[:, 0].astype(float)

    contrast = (np.percentile(gray, 95, axis=0) - np.percentile(gray, 5, axis=0))
    best = contrast.max()

    if best < 8:
        # Uniform bar (0% or 100% full): no mid->light step anywhere, so fall
        # back to columns that simply differ from the background.
        vals, counts = np.unique(np.round(gray), return_counts=True)
        bg = vals[counts.argmax()]
        cols = np.flatnonzero(np.abs(np.median(gray, axis=0) - bg) > 8)
    else:
        cols = np.flatnonzero(contrast >= keep * best)

    if cols.size == 0:
        return np.median(gray, axis=1)
    return np.median(gray[:, cols], axis=1)


def detect_palette(p, min_gap=10.0, merge=8.0):
    """The three dominant shades in the profile, dark -> light.

    Values are clustered before ranking, not simply counted. Screenshot
    compression splits one flat colour across neighbouring values (165 and
    166, say), and taking the three most frequent values raw can return two
    halves of the same shade while dropping a real one entirely.
    """
    vals, counts = np.unique(np.round(p), return_counts=True)
    vals = vals.astype(float)

    clusters = []
    remaining = np.ones(vals.size, bool)
    while remaining.any():
        i = np.flatnonzero(remaining)[np.argmax(counts[remaining])]
        near = remaining & (np.abs(vals - vals[i]) <= merge)
        weight = counts[near].sum()
        clusters.append((weight, float(np.average(vals[near], weights=counts[near]))))
        remaining &= ~near

    if len(clusters) < 3:
        raise ValueError(
            f"only {len(clusters)} distinct shade(s) found — the bar may be "
            f"full or empty, or the crop may miss the background")

    clusters.sort(key=lambda c: -c[0])
    top = np.sort(np.array([c[1] for c in clusters[:3]]))
    if np.diff(top).min() < min_gap:
        raise ValueError(
            f"the three dominant shades {[round(v) for v in top]} are too "
            f"close to be background/remaining/done")
    return top


def cross(p, level, i, j):
    """Sub-pixel position where p crosses `level` between indices i and j."""
    a, b = p[i], p[j]
    if a == b:
        return float(i)
    return i + (level - a) / (b - a) * (j - i)


def find_edges(p, pal, tol):
    """Return (bar_start, boundary, bar_end, done_is_at_high_index)."""
    bg, mid, light = pal
    lab = np.full(p.shape, -1, int)
    for k, v in enumerate(pal):
        lab[np.abs(p - v) <= tol] = k

    solid = np.flatnonzero(lab > 0)
    if solid.size == 0:
        raise SystemExit("no bar found: no pixels matched the mid/light colours")
    lo, hi = solid[0], solid[-1]

    done = np.flatnonzero(lab == 2)
    left = np.flatnonzero(lab == 1)
    if done.size == 0 or left.size == 0:
        return float(lo), (float(lo) if done.size else float(hi + 1)), \
               float(hi + 1), done.size > 0
    high = done.mean() > left.mean()      # which end holds the done colour

    # Outer edges: crossing halfway between background and the solid colour.
    outer_lo = cross(p, (bg + p[lo]) / 2, lo - 1, lo) if lo > 0 else lo - 0.5
    outer_hi = cross(p, (bg + p[hi]) / 2, hi + 1, hi) if hi < len(p) - 1 else hi + 0.5

    # Inner boundary: crossing halfway between mid and light.
    seam = done[0] - 1 if high else done[-1] + 1
    boundary = cross(p, (mid + light) / 2, seam, seam + (1 if high else -1))
    return float(outer_lo), float(boundary), float(outer_hi), high


def measure(image, horizontal=False, fast=False, tol=12.0, strip=8):
    """Measure a bar from a PIL Image.

    Returns (percentage, annotated PIL Image, info dict). Raises ValueError
    if no bar is present, so callers can report that instead of crashing.
    """
    img = np.array(image.convert("RGB"))
    if horizontal:
        img = img.transpose(1, 0, 2)

    p = profile(img.mean(2))
    pal = DEFAULT_PALETTE if fast else detect_palette(p)

    try:
        lo, boundary, hi, high = find_edges(p, pal, tol)
    except SystemExit as e:
        raise ValueError(str(e)) from None
    except (IndexError, ValueError) as e:
        raise ValueError(f"could not locate a bar: {e}") from None

    total = hi - lo
    if total <= 0:
        raise ValueError("degenerate bar span")
    done = (hi - boundary) if high else (boundary - lo)
    pct = 100 * done / total

    h, w, _ = img.shape
    out = np.full((h, w + 2 * strip, 3), 255, np.uint8)
    out[:, strip:strip + w] = img
    for y in range(h):
        if y < lo - 0.5 or y > hi - 0.5:
            continue
        is_done = (y >= boundary) if high else (y < boundary)
        out[y, :strip] = out[y, strip + w:] = (0, 200, 0) if is_done else (220, 0, 0)
    if horizontal:
        out = out.transpose(1, 0, 2)

    info = {"palette": [round(float(v)) for v in pal], "span": (lo, hi),
            "boundary": boundary, "length": total}
    return pct, Image.fromarray(out), info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("-o", "--out", default="checked.png")
    ap.add_argument("--horizontal", action="store_true",
                    help="bar runs left-to-right instead of top-to-bottom")
    ap.add_argument("--fast", action="store_true",
                    help="skip palette detection, use DEFAULT_PALETTE")
    ap.add_argument("--tol", type=float, default=12,
                    help="max distance to a palette value; wider gaps are "
                         "treated as blurred edge and skipped")
    ap.add_argument("--strip", type=int, default=8)
    ap.add_argument("--quiet", action="store_true",
                    help="print only the percentage")
    args = ap.parse_args()

    img = np.array(Image.open(args.image).convert("RGB"))
    if args.horizontal:
        img = img.transpose(1, 0, 2)
    gray = img.mean(2)

    p = profile(gray)
    pal = DEFAULT_PALETTE if args.fast else detect_palette(p)

    if args.fast:
        unmatched = np.mean(np.abs(p[:, None] - pal[None, :]).min(1) > args.tol)
        if unmatched > 0.25:
            print(f"WARNING: {unmatched:.0%} of the profile matches no "
                  f"palette value — re-run without --fast.")

    lo, boundary, hi, high = find_edges(p, pal, args.tol)
    total = hi - lo
    done = (hi - boundary) if high else (boundary - lo)
    pct = 100 * done / total

    # Annotated copy, coloured against the interpolated spans.
    h, w, _ = img.shape
    s = args.strip
    out = np.full((h, w + 2 * s, 3), 255, np.uint8)
    out[:, s:s + w] = img
    for y in range(h):
        if y < lo - 0.5 or y > hi - 0.5:
            continue
        is_done = (y >= boundary) if high else (y < boundary)
        out[y, :s] = out[y, s + w:] = (0, 200, 0) if is_done else (220, 0, 0)
    if args.horizontal:
        out = out.transpose(1, 0, 2)
    Image.fromarray(out).save(args.out)

    if args.quiet:
        print(f"{pct:.2f}")
    else:
        mode = "assumed" if args.fast else "detected"
        print(f"palette [{mode}] : {[round(v) for v in pal]}")
        print(f"bar span        : {lo:.2f} -> {hi:.2f}  ({total:.2f} px)")
        print(f"fill boundary   : {boundary:.2f}")
        print(f"progress        : {pct:.2f}%")
        print(f"written         : {args.out}")


if __name__ == "__main__":
    main()