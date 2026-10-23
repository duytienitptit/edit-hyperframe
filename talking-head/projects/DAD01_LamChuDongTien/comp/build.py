"""Generate comp/index.html from ../edit/{captions,broll,style,music}.json (style bw-film-quote).

Usage:  python3 comp/build.py        (HF_CAPFONT=georgia|times overrides style.caption.font for option sheets)

The speaker source plays whole (no cuts yet): timeline time = source time. B-roll covers the picture only;
the voice runs underneath. All copy, timing and look values live in edit/*.json; never hand-edit index.html.
"""
import html, json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
EDIT = os.path.join(HERE, "..", "edit")
LIB = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "library"))


def load(name, default=None):
    p = os.path.join(EDIT, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


caps, broll, st, music = load("captions.json"), load("broll.json"), load("style.json"), load("music.json")
framing, hls = load("framing.json"), load("highlights.json", {"items": []})
W, H = st["canvas"]["width"], st["canvas"]["height"]
SRC = "assets/graded/dad.mp4"  # look baked by prep_graded.py (edit/grade.json); run it first
ROOT = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                   os.path.join(HERE, "..", "source", "dad.mp4")], capture_output=True, text=True).stdout), 3)
esc = lambda s: html.escape(s, quote=False)
attr = lambda o: html.escape(json.dumps(o), quote=True)
parts, js = [], []

# ---------- speaker (picture + voice) ----------
vfade = 0.3
lane = {"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 1}, {"t": round(ROOT - vfade, 3), "v": 1}, {"t": ROOT, "v": 0}]}]}
parts.append(f'<div id="reframe" class="layer"><div id="cam" class="layer"><video id="speaker" src="{SRC}" data-start="0" data-duration="{ROOT}" '
             f'data-media-start="0" data-track-index="0" data-has-audio="true" playsinline data-automation="{attr(lane)}"></video></div></div>')
# face into the safe-zone focus box: one static framing per camera setup, push-in pivots on the face
for f in framing["speaker"]:
    js.append(f'tl.set("#reframe", {{x: {f["x"]}, y: {f["y"]}, scale: {f["scale"]}, transformOrigin: "0px 0px"}}, {f["from"]});')
    js.append(f'tl.set("#cam", {{transformOrigin: "{f["face"][0]}px {f["face"][1]}px"}}, {f["from"]});')
for row in broll["timeline"]:
    if row["kind"] == "source":  # slow push-in, restarts every time the speaker comes back
        a, b = row["start"], min(row["end"], ROOT)
        js.append(f'tl.fromTo("#cam", {{scale: 1}}, {{scale: {1 + st["pushin"]["speaker"]}, duration: {round(b - a, 3)}, '
                  f'ease: "none", immediateRender: false}}, {a});')

# ---------- b-roll (picture only; graded excerpts from prep_graded.py, which keeps 1 s before the in-point) ----------
for k, row in enumerate(r for r in broll["timeline"] if r["kind"] == "broll"):
    name = f'{row["id"]}_{os.path.basename(row["file"])}'
    a, d = row["start"], round(row["end"] - row["start"], 3)
    parts.append(f'<div id="bw-{row["id"]}" class="layer"><video id="br-{row["id"]}" class="clip" src="assets/graded/{name}" muted playsinline '
                 f'data-start="{a}" data-duration="{d}" data-media-start="{round(min(row["in"], 1.0), 3)}" data-track-index="{1 + k % 2}"></video></div>')
    js.append(f'tl.fromTo("#bw-{row["id"]}", {{scale: 1}}, {{scale: {1 + st["pushin"]["broll"]}, duration: {d}, '
              f'ease: "none", immediateRender: false}}, {a});')

# ---------- highlights: keyword lockups in the safe-zone white box ----------
HL = st["highlight"]
wz = st["safe_zone"]["white"]
KEY_MAX = wz[2] - HL["left"] - 10  # widest key line that still clears the TikTok button column
from fontTools.ttLib import TTFont
_kf = TTFont(os.path.join(HERE, HL["key"]["file"]))
_cmap, _hmtx, _upm = _kf.getBestCmap(), _kf["hmtx"], _kf["head"].unitsPerEm


def key_size(text):
    """Font size that fits the key line in KEY_MAX, measured from the font file so the page needs no async fit."""
    size = HL["key"]["size"]
    adv = sum(_hmtx[_cmap[ord(ch)]][0] for ch in text if ord(ch) in _cmap) / _upm
    width = size * (adv + HL["key"]["letter_spacing"] * len(text)) * 1.02
    return round(size * min(1, KEY_MAX / width), 1)
LEAD_IN = 0.15  # motion starts just before the word so the line is settled as it is spoken
hl_windows, hl_html = [], []
for h in hls["items"]:
    a = round(h["lines"][0]["at"] - LEAD_IN, 3)
    end = min(ROOT, round(h["out"] + HL["exit"], 3))
    hl_windows.append((a, end))
    lines = []
    for i, ln in enumerate(h["lines"]):
        cls = f'hl-line {ln["kind"]}'
        body = f'<span class="in">{esc(ln["text"])}</span>'
        if ln["kind"] == "key":
            body = (f'<span class="in" style="font-size: {key_size(ln["text"])}px"><span class="gold">{esc(ln["text"])}</span>'
                    f'<span class="shine" aria-hidden="true">{esc(ln["text"])}</span></span>')
        lines.append(f'<div class="{cls}" id="{h["id"]}-l{i}"><span class="mask">{body}</span></div>')
        sel, t = f"#{h['id']}-l{i} .in", round(ln["at"] - LEAD_IN, 3)
        # every line waits hidden from the clip start until its own word (later lines must not show early)
        js.append(f'tl.set("{sel}", {{yPercent: 110{", opacity: 0" if ln["kind"] == "lead" else ""}}}, {a});')
        if ln["kind"] == "key":
            js.append(f'tl.fromTo("{sel}", {{yPercent: 110, scaleX: 1.1, scaleY: 1.04}}, '
                      f'{{yPercent: 0, scaleX: 1, scaleY: 1, duration: {HL["reveal"]}, ease: "power3.out", immediateRender: false}}, {t});')
            s0 = round(t + 0.3, 3)  # rule 9: one shine pass right after landing, finished before the exit
            if s0 + 0.55 <= h["out"] - 0.05:
                js.append(f'tl.fromTo("#{h["id"]}-l{i} .shine", {{backgroundPosition: "160% 0"}}, '
                          f'{{backgroundPosition: "-60% 0", duration: 0.55, ease: "power2.inOut", immediateRender: false}}, {s0});')
        else:
            js.append(f'tl.fromTo("{sel}", {{yPercent: 110, opacity: 0}}, {{yPercent: 0, opacity: 1, duration: {HL["reveal"]}, '
                      f'ease: "power3.out", immediateRender: false}}, {t});')
    if h["out"] + HL["exit"] <= ROOT:  # rule 5: gone before the next shot change
        js.append(f'tl.to("#{h["id"]} .hl-box", {{yPercent: -6, opacity: 0, duration: {HL["exit"]}, ease: "power2.in"}}, {h["out"]});')
    hl_html.append(f'<div id="{h["id"]}" class="hl clip" data-start="{a}" data-duration="{round(end - a, 3)}" data-track-index="21">'
                   f'<div class="hl-box">{"".join(lines)}</div></div>')

# ---------- captions: short phrases, hard cut in/out (ref style), 1 line, hidden while a highlight is on ----------
cues = [(c["startMs"] / 1000, c["endMs"] / 1000, c["text"]) for c in caps]
pieces = []
for k, (a, b, text) in enumerate(cues):
    nxt = cues[k + 1][0] if k + 1 < len(cues) else ROOT
    b = nxt if nxt - b < 0.5 else min(b + 0.3, nxt)  # rule 8: close cues switch instantly
    spans = [(a, b)]
    for w0, w1 in hl_windows:
        spans = [s for x0, x1 in spans for s in ((x0, min(x1, w0)), (max(x0, w1), x1)) if s[1] - s[0] > 0]
    pieces += [(round(x0, 3), round(x1, 3), text) for x0, x1 in spans if x1 - x0 >= 0.3]
cap_html = [f'<div id="cap-{k}" class="cap clip" data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="20">'
            f'<span class="cap-in">{esc(text)}</span></div>' for k, (a, b, text) in enumerate(pieces)]
parts.append('<div id="caps">' + "".join(cap_html) + "</div>")
parts.append('<div id="hls">' + "".join(hl_html) + "</div>")

# ---------- music bed ----------
if music:
    m = music
    mlane = {"version": 1, "lanes": [{"target": "volume", "points": [
        {"t": 0, "v": 0}, {"t": m["fade_in"], "v": 1}, {"t": round(ROOT - m["fade_out"], 3), "v": 1}, {"t": ROOT, "v": 0}]}]}
    link = os.path.join(HERE, "assets", "music" + os.path.splitext(m["file"])[1])
    if os.path.lexists(link):
        os.remove(link)
    os.symlink(os.path.relpath(os.path.join(LIB, os.path.relpath(m["file"], "library")), os.path.dirname(link)), link)
    parts.append(f'<audio id="music" src="assets/{os.path.basename(link)}" data-start="0" data-duration="{ROOT}" '
                 f'data-media-start="{m["in"]}" data-track-index="10" data-volume="{m["volume"]}" data-automation="{attr(mlane)}"></audio>')

# ---------- fade to black ----------
js.append(f'tl.fromTo("#fade", {{opacity: 0}}, {{opacity: 1, duration: {st["fade_out"]}, ease: "power1.in", immediateRender: false}}, '
          f'{round(ROOT - st["fade_out"], 3)});')

cap = st["caption"]
font = cap["fonts"][os.environ.get("HF_CAPFONT", cap["font"])]
n_stage = 1 + sum(r["kind"] == "broll" for r in broll["timeline"])
page = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "{font["family"]}"; src: url("{font["file"]}"); font-display: block; }}
      @font-face {{ font-family: "{HL["key"]["family"]}"; src: url("{HL["key"]["file"]}"); font-display: block; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
      #stage {{ position: absolute; inset: 0; }}
      .layer {{ position: absolute; inset: 0; }}
      .layer video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .cap {{ position: absolute; left: 0; right: 0; top: {cap["center_y"] - round(cap["size"] * 0.6)}px; display: flex; justify-content: center; }}
      .hl {{ position: absolute; left: {HL["left"]}px; top: {wz[1] + 24}px; width: {KEY_MAX}px; height: {wz[3] - wz[1] - 24}px; }}
      .hl-box {{ display: flex; flex-direction: column; align-items: flex-start; filter: drop-shadow(0 4px 10px rgba(0,0,0,.55)); }}
      .hl-line {{ display: block; }}
      .hl-line .mask {{ display: block; overflow: hidden; padding: 0.04em 0.04em 0.06em; }}
      .hl-line.key {{ margin: -0.06em 0 -0.12em; }}
      .hl-line .in {{ display: block; position: relative; transform-origin: 0% 100%; white-space: nowrap; }}
      .hl-line.lead .in {{ font-family: "{HL["lead"]["family"]}", Georgia, serif; font-size: {HL["lead"]["size"]}px; color: {HL["lead"]["color"]};
        line-height: 1.15; -webkit-text-stroke: 2px rgba(20,14,4,.85); paint-order: stroke fill; }}
      /* tall line box: background-clip text only paints inside the box, and stacked Vietnamese marks (Ấ, Ể, Ủ) sit above the caps */
      .hl-line.key .in {{ font-family: "{HL["key"]["family"]}", sans-serif; font-size: {HL["key"]["size"]}px; line-height: 1.4;
        letter-spacing: {HL["key"]["letter_spacing"]}em; text-transform: uppercase; }}
      .hl-line.key .gold {{ display: block; color: transparent; -webkit-background-clip: text; background-clip: text;
        background-image: linear-gradient(180deg, {", ".join(HL["key"]["gold"])}); }}
      .hl-line.key .shine {{ position: absolute; inset: 0; color: transparent; -webkit-background-clip: text; background-clip: text;
        background-image: linear-gradient(105deg, transparent 38%, rgba(255,255,255,.95) 50%, transparent 62%);
        background-size: 250% 100%; background-repeat: no-repeat; background-position: 160% 0; }}
      .cap-in {{ font-family: "{font["family"]}", Georgia, serif; font-size: {cap["size"]}px; color: {cap["color"]}; white-space: nowrap;
        max-width: {round(cap["max_width"] * W)}px; -webkit-text-stroke: {cap["stroke_width"]}px {cap["stroke"]}; paint-order: stroke fill;
        text-shadow: 0 2px 6px rgba(0,0,0,.75); line-height: 1.2; }}
      #fade {{ position: absolute; inset: 0; background: #000; opacity: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{ROOT}" data-width="{W}" data-height="{H}">
      <div id="stage">{"".join(parts[:n_stage])}</div>
      {"".join(parts[n_stage:])}
      <div id="fade"></div>
    </div>
    <script>
      // registered synchronously: an async registration (fonts.ready) let the renderer capture before the timeline existed
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + l for l in js).lstrip()}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(page)
print(json.dumps({"root": ROOT, "captions": len(cues), "broll": sum(r["kind"] == "broll" for r in broll["timeline"]),
                  "music": bool(music), "capfont": font["family"]}))
