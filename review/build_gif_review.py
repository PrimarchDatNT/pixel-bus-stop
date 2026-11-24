"""Self-contained review page for the v4 GIF-style styleframe -> review/Tram-Xe-Pixel-GIF.html

Run after `compose/gif_frame.py --anim 24` (uses review/gif_style/frame.png, _frames/, loop.mp4, props_sheet.png,
ai_vs_hand.png)."""
import base64
import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "review/gif_style"
OUT = ROOT / "review/Tram-Xe-Pixel-GIF.html"
FPS = 12


def uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def png(im: Image.Image) -> str:
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); return uri(b.getvalue(), "image/png")


def at(t: float) -> Image.Image:
    """Logical 384x216 frame of the loop at time t (from the rendered 5x frames)."""
    f = Image.open(G / "_frames" / f"{int(round(t * FPS)):05d}.png").convert("RGB")
    return f.resize((f.width // 5, f.height // 5), Image.NEAREST)


def figs(items):
    return "".join(f'<figure class="crop"><img class="px" src="{png(im)}" alt="{t}"><figcaption>{t}</figcaption></figure>'
                   for t, im in items)


frame = Image.open(G / "frame.png").convert("RGB")                       # 384x216 logical, t = 5 s
bus_items = [
    ("4–8 giây: xe buýt chạy vào, phanh chậm dần", at(6.2).crop((150, 120, 384, 216))),
    ("8,5–13,5 giây: xe đỗ che trạm, máy rung nhẹ; mèo mun quay ra nhìn", at(10.5).crop((0, 110, 240, 216))),
    ("13,5 giây: xe chạy đi, ống xả nhả khói", at(14.6).crop((0, 110, 240, 216))),
    ("Bạn học sinh vừa xuống xe đi bộ qua quán", at(17.0).crop((150, 120, 384, 216))),
]
cat_items = [(lbl, at(t).crop((108, 128, 152, 156)).resize((44 * 4, 28 * 4), Image.NEAREST))
             for lbl, t in (("Ngồi", 1.0), ("Liếm chân", 4.1), ("Rửa mặt", 7.6), ("Nhìn xe buýt", 10.0))]
other_items = [("Góc trà đá", frame.crop((300, 150, 384, 202))), ("Bồ câu đậu nóc nhà", frame.crop((200, 22, 300, 56))),
               ("Bồ câu mổ thóc trước quán", frame.crop((226, 176, 312, 202))),
               ("Quán tạp hóa, ông chủ đọc báo", frame.crop((176, 120, 300, 192)))]
video = uri((G / "loop.mp4").read_bytes(), "video/mp4")
ref = uri((ROOT / "refs/pinterest_pixel_shop.gif").read_bytes(), "image/gif")
still = png(frame)
sheet_img = png(Image.open(G / "props_sheet.png"))
ai_img = png(Image.open(G / "ai_vs_hand.png"))

CSS = """
:root{--bg:#f4f2ec;--fg:#1d2326;--mut:#5d676b;--card:#fff;--line:#d9d5cc;--acc:#c2185b}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121719;--fg:#e8ecec;--mut:#9aa6a8;--card:#1b2225;--line:#2c3639;--acc:#f06292}}
:root[data-theme=dark]{--bg:#121719;--fg:#e8ecec;--mut:#9aa6a8;--card:#1b2225;--line:#2c3639;--acc:#f06292}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 "Be Vietnam Pro",system-ui,sans-serif}
main{max-width:1240px;margin:0 auto;padding:32px 16px 80px}h1{font-size:30px;margin:0 0 6px}h2{font-size:21px;margin:40px 0 8px}
p,li{max-width:820px}.mut{color:var(--mut)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
img.px{image-rendering:pixelated;image-rendering:crisp-edges;width:100%;height:auto;display:block}
video{width:100%;display:block;background:#000}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:800px){.two{grid-template-columns:1fr}}
.crops{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px}
.crops.cat{grid-template-columns:repeat(auto-fill,minmax(180px,1fr))}
.crop{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.crop figcaption,.cap{padding:8px 12px;font-size:14px;color:var(--mut)}
.ref img{width:100%;display:block}
table{border-collapse:collapse;font-size:15px}td{padding:4px 14px 4px 0;vertical-align:top}td:first-child{color:var(--mut);white-space:nowrap}
"""

page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trạm Xe Pixel</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><main>
<h1>Trạm Xe Bốn Mùa · khung thử pixel kiểu GIF (bản 4.2)</h1>
<p class="mut">Mùa hạ, trưa nắng. Pixel art vẽ bằng code trên lưới 384×216, phóng ×5 lên 1920×1080. Màu lấy từ GIF tham khảo.
Mọi thứ là lớp riêng nên chuyển động và đổi mùa đều làm được bằng code.</p>

<h2>Chạy thử 24 giây, lặp liền</h2>
<div class="card"><video src="{video}" autoplay loop muted playsinline controls></video>
<div class="cap">Khung cuối nối khít khung đầu, để lặp bao nhiêu lần cũng không bị giật.</div></div>
<table style="margin-top:12px">
<tr><td>0–4 giây</td><td>Mèo mun ngồi trên mái trạm rồi liếm chân. Cô gái bấm điện thoại, bồ câu mổ thóc, người gánh hàng đi qua.</td></tr>
<tr><td>4–8,5 giây</td><td>Xe buýt vào từ bên phải, phanh chậm dần. Mèo rửa mặt.</td></tr>
<tr><td>8,5–13,5 giây</td><td>Xe đỗ trước trạm, máy rung nhẹ. Mèo quay ra nhìn, chớp mắt.</td></tr>
<tr><td>13,5–18,5 giây</td><td>Xe chạy đi, ống xả nhả khói. Phía sau xe lộ ra bạn học sinh vừa xuống, đi bộ qua quán tạp hóa và góc trà đá rồi ra khỏi khung.</td></tr>
<tr><td>18,5–24 giây</td><td>Phố yên trở lại, mèo liếm chân tiếp. Hết vòng thì quay về khung đầu.</td></tr>
</table>

<h2>Xe buýt vào trạm</h2>
<div class="crops">{figs(bus_items)}</div>
<p class="mut">Xe vàng đỏ kiểu xe buýt Hà Nội, có tài xế và khách ngồi trong cửa sổ. Thân xe để trơn, không bảng tuyến, không số, không chữ.
Xe đi bên phải đường nên mình thấy hông bên tài xế; cửa lên xuống nằm ở phía vỉa hè, khuất sau thân xe.
Vì vậy học sinh chỉ hiện ra khi xe chạy đi.</p>

<h2>Mèo mun</h2>
<div class="crops cat">{figs(cat_items)}</div>
<p class="mut">Mèo mun thay cho mèo mướp, ngồi trên mái trạm trước khối hoa giấy để nổi dáng đen. Bé có các động tác ngồi vẫy đuôi, liếm chân, rửa mặt,
quay ra nhìn và chớp mắt vàng. Mèo mướp mình giữ lại để dùng cho mùa khác.</p>

<h2>Khung tĩnh</h2>
<div class="card"><img class="px" src="{still}" alt="Khung tĩnh"></div>

<h2>Phóng to</h2>
<div class="crops">{figs(other_items)}</div>

<h2>Chim và đồ trà đá (phóng ×8)</h2>
<div class="card"><img class="px" src="{sheet_img}" alt="Bảng sprite" style="max-width:520px;margin:0 auto"></div>

<h2>Đặt cạnh GIF tham khảo</h2>
<div class="two"><figure class="card ref" style="margin:0"><img src="{ref}" alt="GIF tham khảo"><figcaption class="cap">GIF anh gửi</figcaption></figure>
<figure class="card" style="margin:0"><img class="px" src="{still}" alt="Bản của mình"><figcaption class="cap">Khung thử của mình</figcaption></figure></div>

<h2>Đã sửa so với bản 3</h2>
<ul>
<li>Thêm xe buýt vào trạm (thân xe trơn, không chữ), đỗ lại rồi chạy đi, có khói ống xả và bánh xe quay theo tốc độ.</li>
<li>Thêm bạn học sinh áo trắng, khăn quàng đỏ, cặp xanh xuống xe rồi đi bộ ra khỏi khung.</li>
<li>Mèo mun thay mèo mướp: ngồi, liếm chân, rửa mặt, nhìn xe buýt.</li>
<li>Video 24 giây lặp liền: mọi chuyển động (người gánh hàng, chim bay, cánh hoa rơi, bồ câu) đều được chỉnh nhịp cho khớp vòng lặp.</li>
</ul>
<h2>Còn yếu</h2>
<ul>
<li>Cô gái vẫn ngồi chờ sau khi xe đi, coi như cô đợi tuyến khác. Nếu muốn cô lên xe, cần thêm cảnh một người mới đi vào ngồi chờ thì video mới lặp được.</li>
<li>Phố xa còn là các khối đơn giản.</li>
</ul>

<h2>Đã thử ComfyUI cho chim và trà đá (bản 3)</h2>
<div class="card"><img src="{ai_img}" alt="ComfyUI so với vẽ tay" style="width:100%;max-width:900px;display:block;margin:0 auto"></div>
<p class="mut">Ảnh AI ở cỡ lớn đẹp, nhưng thu về cỡ thật trong cảnh (chim sẻ 8 điểm ảnh, bồ câu 14) thì nhòe hết.
Nên đồ nhỏ vẫn vẽ tay; ComfyUI chỉ dùng để lấy ý tưởng cho vật lớn.</p>
</main></body></html>"""
OUT.write_text(page, encoding="utf-8")
print(OUT, f"{OUT.stat().st_size / 1e6:.1f} MB")
