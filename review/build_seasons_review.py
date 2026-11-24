"""Self-contained review page for the four-season loops -> review/Tram-Xe-4-Mua.html

Run after `compose/gif_frame.py --all --anim 24` (uses review/gif_style/<season>/_frames, loop.mp4 and bon_mua.mp4)."""
import base64
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "compose"))
G = ROOT / "review/gif_style"
OUT = ROOT / "review/Tram-Xe-4-Mua.html"
FPS = 12


def uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def png(im: Image.Image) -> str:
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); return uri(b.getvalue(), "image/png")


def at(season: str, t: float) -> Image.Image:
    return Image.open(G / season / "_frames" / f"{int(round(t * FPS)) % 288:05d}.png").convert("RGB")


def crop(season, t, box, k=3):
    im = at(season, t).crop(box)
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def best_firework_t():
    """Frame of the winter loop where the fireworks fill the most sky (diff against the frame-to-frame median)."""
    import fx_gif as fx
    best, bt = -1, 0.0
    for i in range(0, 288, 2):
        cv = Image.new("RGBA", (384, 216), (0, 0, 0, 255))
        fx.fireworks(cv, i / FPS, 24.0, region=(262, 10, 380, 112))
        n = int((np.array(cv)[..., :3].sum(axis=-1) > 0).sum())
        if n > best:
            best, bt = n, i / FPS
    return bt


def small_video(src: Path, k=2) -> bytes:
    """Re-encode at x2 (768x432) so the 2-minute montage stays light enough to embed."""
    tmp = G / "_montage_small.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", f"scale={384 * k}:{216 * k}:flags=neighbor",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-r", "24", str(tmp)], check=True)
    return tmp.read_bytes()


fw_t = best_firework_t()
SEASONS = [
    ("xuan", "Xuân · sáng mùng Một Tết", [
        "Trời sáng nhẹ, mây trắng to; hoa giấy nở dày nhất năm.",
        "Nhà treo cờ, băng rôn đỏ “CHÚC MỪNG NĂM MỚI”, hai đèn lồng đỏ; chậu quất có bao lì xì trước quán.",
        "Cô gái mặc áo đỏ; đàn chim én bay lượn thay chim sẻ; cánh đào hồng rơi lẫn cánh hoa giấy.",
        "Sau khi xe buýt đi, một chiếc xe máy chở cây đào chạy ngang phố.",
    ], [("Xe máy chở đào (giây 20)", crop("xuan", 20.6, (150, 120, 384, 216))),
        ("Cờ, băng rôn, đèn lồng, quất", crop("xuan", 1.0, (150, 88, 340, 200)))]),
    ("ha", "Hạ · trưa nắng", [
        "Bản đã duyệt: nắng trưa, hoa giấy hồng rực, bồ câu, chim sẻ, góc trà đá.",
    ], [("Xe buýt đỗ, mèo mun nhìn xe", crop("ha", 10.5, (0, 110, 240, 216)))]),
    ("mua", "Hạ · mưa rào", [
        "Trời xám, mây nặng, mưa rào; cả cảnh tối và ngả xám, quán vẫn sáng.",
        "Mèo mun xuống trú mưa trên ghế chờ, ngồi cạnh cô gái; dưới mái trạm không có mưa.",
        "Người gánh hàng mặc áo mưa xanh, bạn học sinh mặc áo mưa vàng; chim và ông uống trà đi trú.",
    ], [("Mèo trú mưa trên ghế chờ", crop("mua", 2.0, (0, 130, 250, 216))),
        ("Học sinh áo mưa vàng", crop("mua", 16.5, (150, 120, 384, 216)))]),
    ("thu", "Thu · tối Trung Thu", [
        "Hoàng hôn tím cam, trăng rằm to ở góc phải; cửa sổ và quán lên đèn vàng.",
        "Đèn ông sao treo trước quán, đèn lồng đỏ ở mái trạm, tất cả đều phát sáng.",
        "Đoàn múa lân (lân, ông Địa cầm quạt, bạn nhỏ đánh trống) đi ngang phố.",
        "Hai bạn nhỏ xuống xe buýt cầm đèn ông sao; lá vàng bay; hoa giấy thưa dần, lộ lá xanh.",
    ], [("Đoàn múa lân", crop("thu", 3.0, (60, 140, 300, 216))),
        ("Trẻ cầm đèn ông sao", crop("thu", 17.0, (150, 110, 384, 216))),
        ("Trăng rằm", crop("thu", 1.0, (284, 0, 384, 80)))]),
    ("dong", "Đông · đêm Giao thừa sương mù", [
        "Đêm xanh thẫm có sao; pháo hoa nổ phía sau nhà, trên thành phố xa; sương mù trôi chậm.",
        "Quán và hai cửa sổ sáng đèn, dây đèn nháy dưới ban công; xe buýt sáng đèn trong khoang.",
        "Mèo mun vẫn ngồi trên mái, mắt vàng sáng trong đêm.",
        "Mọi người mặc áo ấm: cô gái áo phao hồng, ông uống trà áo bộ đội; chim đã đi ngủ.",
    ], [("Pháo hoa", crop("dong", fw_t, (230, 0, 384, 140))),
        ("Quán đêm, dây đèn nháy", crop("dong", 2.0, (150, 96, 310, 200))),
        ("Mèo mun mắt sáng", crop("dong", 2.0, (100, 120, 160, 160), k=5))]),
]

CSS = """
:root{--bg:#f4f2ec;--fg:#1d2326;--mut:#5d676b;--card:#fff;--line:#d9d5cc;--acc:#c2185b}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121719;--fg:#e8ecec;--mut:#9aa6a8;--card:#1b2225;--line:#2c3639;--acc:#f06292}}
:root[data-theme=dark]{--bg:#121719;--fg:#e8ecec;--mut:#9aa6a8;--card:#1b2225;--line:#2c3639;--acc:#f06292}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 "Be Vietnam Pro",system-ui,sans-serif}
main{max-width:1240px;margin:0 auto;padding:32px 16px 80px}h1{font-size:30px;margin:0 0 6px}h2{font-size:23px;margin:48px 0 8px}
p,li{max-width:860px}.mut{color:var(--mut)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
img.px{image-rendering:pixelated;image-rendering:crisp-edges;width:100%;height:auto;display:block}
video{width:100%;display:block;background:#000;image-rendering:pixelated}
.crops{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin-top:14px}
.crop{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.crop figcaption,.cap{padding:8px 12px;font-size:14px;color:var(--mut)}
.grid4{display:grid;grid-template-columns:1fr 1fr;gap:10px}@media(max-width:700px){.grid4{grid-template-columns:1fr}}
.grid4 figure{margin:0}
table{border-collapse:collapse;font-size:15px}td{padding:4px 14px 4px 0;vertical-align:top}td:first-child{color:var(--mut);white-space:nowrap}
"""

montage_src = G / "bon_mua.mp4"
montage = uri(small_video(montage_src), "video/mp4")
stills = "".join(
    f'<figure class="card"><img class="px" src="{png(at(k, 10.5 if k != "dong" else fw_t))}" alt="{t}">'
    f'<figcaption class="cap">{t}</figcaption></figure>' for k, t, _, _ in SEASONS)
sections = []
for k, title, notes, crops in SEASONS:
    vid = uri((G / k / "loop.mp4").read_bytes(), "video/mp4")
    lis = "".join(f"<li>{n}</li>" for n in notes)
    figs = "".join(f'<figure class="crop"><img class="px" src="{png(im)}" alt="{c}"><figcaption>{c}</figcaption></figure>'
                   for c, im in crops)
    sections.append(f'<h2 id="{k}">{title}</h2><div class="card"><video src="{vid}" loop muted playsinline controls preload="metadata"></video>'
                    f'<div class="cap">Vòng lặp 24 giây, nối khít.</div></div><ul>{lis}</ul><div class="crops">{figs}</div>')

page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trạm Xe Bốn Mùa</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><main>
<h1>Trạm Xe Bốn Mùa · bốn mùa (bản 5)</h1>
<p class="mut">Cùng một góc phố, cùng nhịp 24 giây (xe buýt vào trạm giây 4, đỗ đến giây 13,5 rồi chạy, mèo mun phản ứng theo xe).
Mỗi mùa đổi trời, ánh sáng, cây hoa giấy, quần áo, đồ trang trí và người qua đường. Ánh sáng tối và đèn được làm theo kiểu pixel:
mỗi màu đổi thành đúng một màu mới nên mảng phẳng vẫn phẳng, đèn sáng là các vòng sáng phẳng.</p>

<h2>Bốn mùa nối nhau (2 phút)</h2>
<div class="card"><video src="{montage}" autoplay loop muted playsinline controls></video>
<div class="cap">Xuân → Hạ nắng → Hạ mưa → Thu → Đông, mỗi đoạn 24 giây, chuyển mùa bằng hiệu ứng ô pixel tan dần. Bản này thu nhỏ ×2 cho nhẹ; file đầy đủ 1920×1080: review/gif_style/bon_mua.mp4</div></div>

<h2>Bốn mùa cạnh nhau</h2>
<div class="grid4">{stills}</div>

{''.join(sections)}

<h2>Còn yếu / cần anh quyết</h2>
<ul>
<li>Mưa rào đang là mùa thứ năm (Hạ có hai trạng thái nắng và mưa). Nếu anh chỉ muốn đúng bốn đoạn thì mình gộp mưa vào cuối đoạn hạ.</li>
<li>Mỗi mùa hiện mới có một vòng 24 giây. Video dài (ví dụ 1 tiếng) sẽ lặp mỗi mùa nhiều vòng rồi mới chuyển mùa.</li>
<li>Pháo hoa vẽ bằng chấm và vệt, chưa có tiếng. Âm thanh (mưa, tiếng trống lân, pháo) mình chưa làm.</li>
</ul>
</main></body></html>"""
OUT.write_text(page, encoding="utf-8")
print(OUT, f"{OUT.stat().st_size / 1e6:.1f} MB", "fireworks t =", fw_t)
