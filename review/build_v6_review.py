"""Self-contained review page for bản 6 (kiosk + park) -> review/Tram-Xe-Cong-Vien.html (bản 6b, café)

Run after
    compose/gif_frame.py --scene cafe --all --anim 24
    compose/gif_frame.py --scene taphoa --all --anim 24
Loops are re-encoded at x2 (768x432) so the page stays light; the full 1920x1080 files are listed on the page."""
import base64
import io
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "compose"))
import gif_frame as gf  # noqa: E402
G = ROOT / "review/gif_style"
OUT = ROOT / "review/Tram-Xe-Cong-Vien.html"
TMP = G / "_v6_tmp"; TMP.mkdir(exist_ok=True)
FPS = 12
SEASONS = [("xuan", "Xuân · sáng mùng Một Tết"), ("ha", "Hạ · trưa nắng"), ("mua", "Hạ · mưa rào"),
           ("thu", "Thu · tối Trung Thu"), ("dong", "Đông · đêm Giao thừa")]


def uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def png(im: Image.Image) -> str:
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); return uri(b.getvalue(), "image/png")


def jpg(im: Image.Image) -> str:
    b = io.BytesIO(); im.save(b, "JPEG", quality=92); return uri(b.getvalue(), "image/jpeg")


def at(path: Path, t: float) -> Image.Image:
    return Image.open(path / "_frames" / f"{int(round(t * FPS)) % 288:05d}.png").convert("RGB")


def at_hi(path: Path, t: float, size=(960, 540)) -> Image.Image:
    """Full-resolution frame (soft sky restored), shrunk for the page; 960 = 1920 / 2 keeps the pixels even."""
    im = Image.fromarray(gf.hi_frame(path, int(round(t * FPS)) % 288))
    return im.resize(size, Image.BOX)


def crop(path, t, box, k=3):
    im = at(path, t).crop(box)
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def small(src: Path, name: str, k=2, crf=20, t=None) -> str:
    dst = TMP / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src)] + (["-t", str(t)] if t else []) + [ "-vf", f"scale={384 * k}:{216 * k}:flags=area",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf), "-r", "24", str(dst)], check=True)
    return uri(dst.read_bytes(), "video/mp4")


CAFE, TAPHOA = G / "v6_cafe", G / "v6_taphoa"

CSS = """
:root{--bg:#f4f2ec;--fg:#1d2326;--mut:#5d676b;--card:#fff;--line:#d9d5cc;--acc:#2e794d}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121719;--fg:#e8ecec;--mut:#9aa6a8;--card:#1b2225;--line:#2c3639;--acc:#7fbf6a}}
:root[data-theme=dark]{--bg:#121719;--fg:#e8ecec;--mut:#9aa6a8;--card:#1b2225;--line:#2c3639;--acc:#7fbf6a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 "Be Vietnam Pro",system-ui,sans-serif}
main{max-width:1240px;margin:0 auto;padding:32px 16px 80px}h1{font-size:30px;margin:0 0 6px}h2{font-size:23px;margin:48px 0 8px}
h3{font-size:18px;margin:0;padding:10px 12px 0}p,li{max-width:860px}.mut{color:var(--mut)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
img.px{image-rendering:pixelated;image-rendering:crisp-edges;width:100%;height:auto;display:block}
video{width:100%;display:block;background:#000;image-rendering:pixelated}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:760px){.two{grid-template-columns:1fr}}
.two figure,.grid figure{margin:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:10px}
.cap{padding:8px 12px;font-size:14px;color:var(--mut)}
.pick{border:2px solid var(--acc)}
.tag{display:inline-block;font-size:12px;font-weight:600;color:var(--acc);border:1px solid var(--acc);border-radius:99px;padding:0 8px;margin-left:6px;vertical-align:2px}
"""

def bike_sheet(k=3):
    ims = [Image.open(ROOT / f"assets/out_gif/actors/bike_flowers_{v}.png").convert("RGBA").crop((0, 0, 64, 44))
           for v in ("xuan", "ha", "thu", "dong")]
    sheet = Image.new("RGBA", (4 * 68, 44), (85, 89, 95, 255))
    for i, im in enumerate(ims):
        sheet.alpha_composite(im, (i * 68 + 2, 0))
    return sheet.convert("RGB").resize((sheet.width * k, sheet.height * k), Image.NEAREST)


# --- new in 6c: toy-style bus, wooden benches, tea corner without the pipe (+ 6b: grandma, tabby, towers)


def on_bg(im, bg=(214, 210, 200), k=4):
    b = Image.new("RGBA", im.size, bg + (255,)); b.alpha_composite(im)
    return b.convert("RGB").resize((im.width * k, im.height * k), Image.NEAREST)


bus_new = Image.open(ROOT / "assets/out_gif/actors/bus32.png").convert("RGBA").crop((0, 0, 148, 58))
cmp_html = f"""
<div class="two">
<figure class="card"><img class="px" src="{png(crop(CAFE / 'ha', 10.5, (0, 140, 200, 216), 4))}" alt="Xe buýt mới ở trạm">
<figcaption class="cap">Xe buýt vẽ lại theo kiểu ảnh mẫu: thân ngắn mập, đầu xe quay chéo ra ngoài, kính dài có vệt sáng trắng chéo, thấy tay vịn và khách bên trong, bánh to có chấm đỏ giữa, đèn pha hình mũi tên cam. Vẫn màu vàng đỏ Hà Nội, không chữ, không số tuyến.</figcaption></figure>
<figure class="card"><img class="px" src="{png(on_bg(bus_new))}" alt="Sprite xe buýt">
<figcaption class="cap">Xe buýt riêng (148×58 điểm ảnh). Bảng đích ở đầu xe chỉ có vạch đèn, không chữ.</figcaption></figure>
<figure class="card"><img class="px" src="{png(crop(CAFE / 'ha', 2.0, (36, 150, 180, 200), 4))}" alt="Mèo mun ngủ trên ghế">
<figcaption class="cap">Mèo mun nằm ngủ ở đầu phải băng ghế gỗ (thở phập phồng, thỉnh thoảng vẫy đuôi). Trạm không còn bảng tên.</figcaption></figure>
<figure class="card"><img class="px" src="{png(crop(CAFE / 'ha', 10.5, (0, 140, 200, 216), 4))}" alt="Mèo mun nhìn xe buýt">
<figcaption class="cap">Xe buýt tới thì mèo ngẩng đầu nhìn, chớp mắt; xe đi thì quay đầu nhìn theo rồi lại nằm ngủ. Xe đỗ sát mép trái nên không che mèo.</figcaption></figure>
<figure class="card"><img class="px" src="{png(crop(CAFE / 'ha', 21.0, (20, 150, 200, 216), 4))}" alt="Xe đạp hoa">
<figcaption class="cap">Xe đạp hoa (vẽ lại, nhiều hoa hơn): cô bán hoa đội nón lá đạp chiếc xe đạp nữ kiểu cũ; sau yên là thúng tre chất hoa cao ngang nón, trước ghi đông có giỏ hoa thứ hai. Cô đi ngang đường lúc không có xe buýt.</figcaption></figure>
<figure class="card"><img class="px" src="{png(bike_sheet())}" alt="Bốn xe hoa theo mùa">
<figcaption class="cap">Mỗi mùa chở đúng loại hoa Hà Nội: Tết cành đào + hồng đỏ · hè hoa sen + hướng dương (trời mưa cô mặc áo mưa xanh) · thu cúc vàng + thạch thảo tím · đông cúc họa mi + hồng đỏ. Tối thì đèn xe sáng.</figcaption></figure>
</div>
"""


SK = G / "_sky_soft"
clouds_html = '<div class="two">' + "".join(
    f'<figure class="card"><img style="width:100%;height:auto;display:block" src="{jpg(Image.open(SK / f"cmp_{st}_{k}.png").convert("RGB").resize((960, 540), Image.BOX))}" alt="{lab} {k}">'
    f'<figcaption class="cap">{lab} · {name}</figcaption></figure>'
    for k, name in (("thu", "Trung Thu"), ("xuan", "sáng Tết"), ("mua", "mưa"))
    for st, lab in (("pixel", "Mây pixel kiểu ảnh mẫu (bản mới)"), ("soft", "Mây mềm (bản trước)"))) + "</div>"


def vframe(src: Path, t: float) -> Image.Image:
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", "-f", "image2pipe",
                        "-vcodec", "png", "-"], capture_output=True, check=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB").resize((960, 540), Image.BOX)


GUSTS = [(46.4, "Hạ nắng → hạ mưa, đầu cơn gió"), (47.1, "Hạ nắng → hạ mưa, mép gió qua giữa khung"),
         (94.6, "Thu → Đông, lá bàng đỏ bay theo gió"), (95.2, "Thu → Đông, gió sắp qua hết")]
gust_html = '<div class="two">' + "".join(
    f'<figure class="card"><img style="width:100%;height:auto;display:block" src="{jpg(vframe(CAFE / "bon_mua.mp4", t))}" alt="{c}">'
    f'<figcaption class="cap">{c} (giây {t:g} của video 4 mùa)</figcaption></figure>' for t, c in GUSTS) + "</div>"


def season_grid(base: Path):
    figs = []
    for k, title in SEASONS:
        t = 10.5 if k != "dong" else 2.5
        figs.append(f'<figure class="card"><img style="width:100%;height:auto;display:block" src="{jpg(at_hi(base / k, t))}" alt="{title}"><figcaption class="cap">{title}</figcaption></figure>')
    return '<div class="grid">' + "".join(figs) + "</div>"


NOTES = {
    "xuan": "Hai đèn lồng đỏ dưới mái, cờ cắm trên cột đèn công viên, chậu quất trước quán. Cây bàng ra lộc non xanh nhạt.",
    "ha": "Nắng trưa. Cây xà cừ to sau mái quán, cây bàng tán tầng bên phải, bãi cỏ và lối dạo, cột đèn ba bóng, nhà cao tầng mờ ở xa; xe đạp hoa chạy ngang.",
    "mua": "Mưa rào, trời xám; quán vẫn sáng, mèo mướp vẫn ngồi trên quầy; mèo mun ngủ trên ghế chờ dưới mái trạm.",
    "thu": "Hoàng hôn Trung Thu, trăng rằm. Cây bàng chuyển vàng cam, lá vàng bay. Đèn ông sao dưới mái, đèn tường và đèn công viên sáng, chữ biển sáng.",
    "dong": "Đêm Giao thừa: cây bàng đỏ lá (đúng kiểu bàng Hà Nội mùa đông), dây đèn nháy dọc mái, đèn tường, đèn công viên, pháo hoa trên tán cây, sương mù.",
}
sections = []
for k, title in SEASONS:
    vid = small(CAFE / k / "loop.mp4", f"cafe_{k}", t=24)
    sections.append(f'<h2 id="{k}">{title}</h2><div class="card"><video src="{vid}" loop playsinline controls preload="metadata"></video>'
                    f'<div class="cap">Trên trang chỉ để 24 giây đầu cho nhẹ (khi lặp lại, mây sẽ nhảy về chỗ cũ). File đầy đủ dài 2 phút, lặp khít cả mây: review/gif_style/v6_cafe/{k}/loop.mp4. {NOTES[k]}</div></div>')

montage_cafe = small(CAFE / "bon_mua.mp4", "cafe_montage", crf=22)

page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trạm Xe Công Viên</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><main>
<h1>Trạm Xe Bốn Mùa · quán cà phê cạnh công viên (bản 6c)</h1>
<p class="mut"><b>Mới nhất:</b> easter egg. Trong cảnh hè, cứ 2 phút có một chuyến là xe buýt iKame thay cho xe 32: thân kem sọc cam vàng, đuôi xe dán linh vật iKame (mặt cười ^^), biển tuyến 35 (API 35), robot Android ngồi trong xe vẫy tay khi xe đỗ. Video 4 mùa có đúng chuyến này. Không có chữ nào.</p>
<p class="mut">Đợt trước: chuyển mùa bằng cơn gió thay cho vỡ ô vuông, kèm tiếng gió.</p>
<p class="mut">Đợt trước: mây vẽ lại theo ảnh mẫu (chùm bông pixel), mây trôi chậm, nền trời gradient.</p>
<p class="mut">Đợt trước: mây mềm vẽ ở 1920×1080. Bản đó vẫn giữ, đổi lại chỉ cần một dòng (xem phần so sánh bên dưới).</p>
<p class="mut">Đợt này: thêm âm thanh. Nhạc lofi 80 BPM (đàn điện Rhodes, bass, trống nhẹ, tiếng đĩa than lạo xạo)
với giai điệu kiểu đàn bầu, mỗi mùa một vòng hợp âm riêng (đông dùng hộp nhạc). Tiếng động khớp với hình: xe buýt tới từ bên phải,
phanh, xì hơi, mở đóng cửa, nổ máy chạy sang trái; chuông xe đạp hoa; xe máy chở đào; chim sẻ, bồ câu, chim én; tách chén và hơi máy pha
trong quán; ve sầu mùa hè; mưa rào và sấm; gió, dế và trống lân mùa thu; pháo hoa và chuông chùa xa đêm Giao thừa. Mỗi vòng 24 giây lặp
khít cả tiếng lẫn hình. Tất cả âm thanh đều do máy tổng hợp, không dùng file có bản quyền.</p>

<h2>Mây pixel (mới) và mây mềm (trước)</h2>
{clouds_html}

<h2>Có gì mới ở các đợt trước</h2>
{cmp_html}

<h2>Bốn mùa nối nhau (2 phút) · có âm thanh</h2>
<p class="mut">Video tự chạy ở chế độ tắt tiếng (trình duyệt bắt buộc vậy): bấm biểu tượng loa trên video để nghe. Các video từng mùa bên dưới bấm play là có tiếng.</p>
<div class="card"><video src="{montage_cafe}" autoplay loop muted playsinline controls></video>
<div class="cap">Xuân → Hạ nắng → Hạ mưa → Thu → Đông. Bản thu nhỏ ×2; file đầy đủ 1920×1080: review/gif_style/v6_cafe/bon_mua.mp4</div></div>
<h3 style="padding:16px 0 8px">Chuyển mùa bằng cơn gió</h3>
{gust_html}
<div style="margin-top:12px">{season_grid(CAFE)}</div>

{''.join(sections)}

<h2>Ghi chú</h2>
<ul>
<li>Xe đạp hoa đi ngang từ giây 18,7 đến giây 3,8 của vòng sau (lúc đường không có xe buýt). Ở cảnh Tết, xe hoa và xe máy chở đào đi ngược chiều nhau.</li>
<li>Bản tạp hóa vẫn giữ trong review/gif_style/v6_taphoa nếu sau này anh muốn đổi lại.</li>
</ul>
</main></body></html>"""
OUT.write_text(page, encoding="utf-8")
print(OUT, f"{OUT.stat().st_size / 1e6:.1f} MB")
