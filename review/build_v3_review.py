"""Self-contained review page for style v3: season plates + sprite cutouts (images embedded as base64).
Usage: .venv/bin/python review/build_v3_review.py   -> review/Tram-Xe-V3.html"""
import base64
import html
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review/Tram-Xe-V3.html"
PL = ROOT / "assets/out_v3/plates"
SP = ROOT / "assets/out_v3/sprites"

PLATES = [  # (file, title, note)
    ("night_rain.png", "Đêm mưa · khung chuẩn", "Bố cục gốc. Mưa, gợn nước, xe chạy sẽ là lớp động bằng code."),
    ("xuan_morning.png", "Xuân · sáng sớm", "Đèn lồng, câu đối, chậu đào quất sẽ là lớp đồ trang trí riêng."),
    ("ha_noon.png", "Hạ · trưa nắng", "Hoa giấy nở rộ, nắng loang qua lá."),
    ("thu_afternoon.png", "Thu · chiều vàng", "Lá vàng phủ mái, lá rụng trên đường; gió thổi lá bay bằng code."),
    ("dong_fog.png", "Đông · sương mù", "Hoa giấy thưa, trời xám, mưa phùn và sương trôi bằng code."),
]


DRAFT_NOTE = {
    "xuan_morning.png": "Bản này mặt đường bị thành lối mòn, nhà còn lốm đốm trắng.",
    "dong_fog.png": "Bản này AI vẽ tuyết phủ mái, sai với Hà Nội; bản mới đã chặn tuyết.",
}


def b64(im: Image.Image, fmt="JPEG", **kw) -> str:
    buf = io.BytesIO()
    im.save(buf, fmt, **kw)
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode()}"


def plate_cards():
    out = []
    for f, title, note in PLATES:
        p = PL / f
        if not p.exists():
            drafts = sorted((PL / "_cand").glob(f.replace(".png", "_v3_*.png")), key=lambda q: q.stat().st_mtime)
            if not drafts:
                continue
            p = drafts[-1]
            title += " · bản nháp"
            note = "Đang sinh lại bản sửa. " + DRAFT_NOTE.get(f, "")
        im = Image.open(p).convert("RGB")
        im = im.resize((1600, round(1600 * im.height / im.width)), Image.LANCZOS)
        out.append(f'<figure class="plate"><img loading="lazy" src="{b64(im, quality=86)}" alt="{html.escape(title)}">'
                   f'<figcaption><b>{html.escape(title)}</b><span>{html.escape(note)}</span></figcaption></figure>')
    return "\n".join(out)


def sprite_cards(group):
    d = SP / group
    man = {}
    mf = d / "manifest.json"
    if mf.exists():
        try:
            for e in json.loads(mf.read_text()):
                man[Path(e.get("file", e.get("name", ""))).stem] = e
        except Exception:
            pass
    out = []
    for p in sorted(d.glob("*.png")):
        if p.name.startswith("_"):
            continue
        im = Image.open(p).convert("RGBA")
        im.thumbnail((360, 260), Image.LANCZOS)
        note = man.get(p.stem, {}).get("notes", "")
        out.append(f'<figure class="sprite"><div class="chk"><img loading="lazy" src="{b64(im, "PNG", optimize=True)}" alt="{p.stem}"></div>'
                   f'<figcaption><b>{p.stem}</b>{f"<span>{html.escape(str(note))}</span>" if note else ""}</figcaption></figure>')
    return "\n".join(out) or '<p class="empty">Chưa có sprite.</p>'


CSS = """
:root{--bg:#f4f2ec;--fg:#1d2326;--mut:#5d676b;--card:#ffffff;--line:#d9d5cc;--acc:#c2185b;--chk1:#e7e3da;--chk2:#d6d1c6}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121719;--fg:#e8ecec;--mut:#9aa6a8;--card:#1b2225;--line:#2c3639;--acc:#f06292;--chk1:#273033;--chk2:#1f272a}}
:root[data-theme=dark]{--bg:#121719;--fg:#e8ecec;--mut:#9aa6a8;--card:#1b2225;--line:#2c3639;--acc:#f06292;--chk1:#273033;--chk2:#1f272a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 "Be Vietnam Pro",system-ui,sans-serif}
main{max-width:1240px;margin:0 auto;padding:32px 16px 80px}h1{font-size:30px;margin:0 0 6px}h2{font-size:21px;margin:44px 0 6px}
.lead,.sub{color:var(--mut);margin:0 0 18px;max-width:780px}
.plates{display:grid;gap:22px}.plate{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.plate img{display:block;width:100%;height:auto}.plate figcaption{padding:10px 14px;display:flex;gap:12px;flex-wrap:wrap;align-items:baseline}
figcaption span{color:var(--mut);font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.sprite{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.chk{height:200px;display:flex;align-items:center;justify-content:center;padding:10px;
background:repeating-conic-gradient(var(--chk1) 0 25%,var(--chk2) 0 50%) 0 0/18px 18px}
.chk img{max-width:100%;max-height:100%}.sprite figcaption{padding:8px 10px;font-size:14px;display:flex;flex-direction:column;gap:2px}
.sprite figcaption b{font-family:ui-monospace,monospace;font-size:13px}.empty{color:var(--mut)}
ol li{margin:6px 0}
"""


def main():
    page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trạm Xe Bốn Mùa v3</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><main>
<h1>Trạm Xe Bốn Mùa · bản v3</h1>
<p class="lead">Phong cách lofi anime tối giản như anh đã chốt: khung ngang 16:9, nhà ống Hà Nội mờ phía sau. Nền vẽ bằng ComfyUI trên laptop MSI.
Dãy nhà giống hệt nhau ở mọi mùa vì máy quay đứng yên. Những thứ chuyển động (mưa, lá bay, xe, người, mèo) sẽ là lớp riêng, chuyển động bằng code.</p>
<h2>Phối cảnh theo mùa</h2>
<div class="plates">{plate_cards()}</div>
<h2>Xe cộ</h2><p class="sub">Đã tách nền, chưa chỉnh màu theo cảnh. Khi ghép, code sẽ phủ màu đêm, mưa, hoàng hôn lên sprite.</p>
<div class="grid">{sprite_cards("vehicles")}</div>
<h2>Người, mèo, chim, lễ hội</h2>
<div class="grid">{sprite_cards("characters")}</div>
</main></body></html>"""
    OUT.write_text(page, encoding="utf-8")
    print(OUT, f"{OUT.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    main()
