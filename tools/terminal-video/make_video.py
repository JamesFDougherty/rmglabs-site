#!/usr/bin/env python3
"""Render a scripted PowerShell-style terminal clip to MP4 (plus a poster JPG).

Usage: python3 make_video.py scenarios/<name>.json ../../blog/videos/<name>.mp4

Frames are drawn deterministically from the scenario (no real vCenter is used),
so every clip is SAMPLE OUTPUT built from simulated lab data. The badge in the
video says so. Needs: python3 + playwright (chromium) and ffmpeg.
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

FPS = 15


def table(cols, rows):
    """Format like PowerShell Format-Table -AutoSize. cols: [{"h":..,"align":"l"|"r"}]"""
    widths = [max(len(c["h"]), *(len(str(r[i])) for r in rows)) for i, c in enumerate(cols)]

    def fmt(vals):
        out = []
        for i, c in enumerate(cols):
            v = str(vals[i])
            out.append(v.rjust(widths[i]) if c.get("align") == "r" else v.ljust(widths[i]))
        return " ".join(out).rstrip()

    lines = [""]
    lines.append(fmt([c["h"] for c in cols]))
    lines.append(fmt(["-" * len(c["h"]) for c in cols]))
    lines += [fmt(r) for r in rows]
    lines.append("")
    return lines


def expand(scen):
    for st in scen["steps"]:
        if st["type"] == "table":
            st["type"] = "out"
            st["lines"] = table(st.pop("cols"), st.pop("rows"))
    return scen


def main(scen_path, out_mp4):
    scen = expand(json.loads(Path(scen_path).read_text(encoding="utf-8")))
    html = (Path(__file__).parent / "player.html").resolve().as_uri()
    out_mp4 = Path(out_mp4)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(html)
        pg.evaluate("document.fonts.ready")
        pg.evaluate("s => init(s)", scen)
        total = pg.evaluate("TOTAL")
        n = int(total / 1000 * FPS)
        for i in range(n + 1):
            pg.evaluate(f"seek({i * 1000 / FPS})")
            pg.screenshot(path=os.path.join(tmp, f"f{i:05d}.png"))
        b.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%05d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24", "-preset", "slow",
                        "-movflags", "+faststart", "-an", str(out_mp4)], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(tmp, f"f{n:05d}.png"),
                        "-q:v", "3", str(out_mp4.with_suffix(".jpg"))], check=True)
    print(out_mp4, f"{total/1000:.1f}s", f"{out_mp4.stat().st_size//1024} KB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
