# Trạm Xe Bốn Mùa — kế hoạch sản xuất

Video pixel art "nửa tĩnh nửa động": máy quay cố định đứng bên này đường, nhìn sang một trạm xe buýt
Hà Nội có ghế nhựa, cây hoa giấy mọc trùm lên mái. Cảnh nền không bao giờ đổi; bốn mùa được kể bằng
ánh sáng, thời tiết, đồ trang trí và những thứ đi ngang qua khung hình.

## 1. Thông số
| | |
|---|---|
| Khung logic | 480×270 px, phóng nguyên ×4 → **1920×1080** (×8 → 4K nếu cần) |
| FPS | 30 fps cho cảnh; sprite chạy nhịp riêng (đi bộ 8, xe 12, idle 3–4) |
| Thời lượng | ~4:00 một vòng, **loop liền** (cuối đông nối thẳng về đầu xuân) → kéo dài 1h cho YouTube bằng ffmpeg |
| Phối cảnh | Nhìn ngang (side view) hơi chúc xuống; trạm xe giữa-trái khung, dãy nhà ống phía sau (đã bỏ cột điện theo góp ý), cây bàng bên phải, vỉa hè gần máy là sân khấu của con mèo |
| Bảng màu | Endesga 32 + 13 màu riêng (dải hồng hoa giấy, xám bê tông, ánh đèn) — khoá cứng bằng validator |

## 2. Kịch bản (≈60 s mỗi mùa)
**Xuân / Tết (0:00–0:58)** — sáng sớm pastel, mưa bụi lất phất. Câu đối đỏ trên cột trạm, đèn lồng đỏ đung đưa
dưới mái, cờ trên ban công, băng rôn "CHÚC MỪNG NĂM MỚI" căng qua dây điện, chậu quất + đào cạnh trạm.
Hoa giấy mới nhú nụ. Chim én bay qua. Xe máy chở cành đào, chở cây quất; cô gái áo dài đỏ đi bộ.
Xe buýt số 32 vào trạm, mở cửa, người lên xuống. Mèo vàng đi vào khung, ngồi xuống, liếm chân.

**Hạ (1:00–1:58)** — trưa nắng gắt, không khí rung vì nóng, ve kêu. Hoa giấy **nở rực** phủ kín mái.
Người đi xe máy mặc áo chống nắng, khẩu trang. Mèo nằm duỗi. 1:15 mây đen kéo tới, trời tối sầm →
**mưa rào**: mưa nặng hạt, nước bắn tung, vũng nước, người chạy vào trạm lấy túi che đầu, xe máy áo mưa
cánh dơi phấp phới, mèo chạy biến. 1:45 tạnh mưa, nắng xuyên mây, mặt đường loáng nước lấp lánh, cầu vồng.

**Thu (2:00–2:58)** — chiều vàng, gió lớn: từng đợt gió **thổi bay cánh hoa giấy và lá bàng vàng** bay ngang
khung. Mèo vồ chiếc lá rơi. Hoàng hôn → tối: đèn đường bật, cửa sổ sáng, trăng rằm lên, dây đèn lồng
giăng mái trạm. **Đoàn rước đèn Trung Thu** đi dọc vỉa hè: trẻ con cầm đèn ông sao, đèn cá chép, múa lân
có trống và Ông Địa phe phẩy quạt, **múa rồng** uốn lượn giữa lòng đường.

**Đông — Hà Nội (3:00–3:58)** *(đề xuất, chờ anh duyệt)* — chiều xám, gió mùa, **mưa phùn + sương mù**
trôi từng dải, người mặc áo phao quàng khăn, thở ra khói. Gánh **ngô khoai nướng** ngồi cạnh trạm, than đỏ
rực, khói bốc. **Xe đạp chở cúc họa mi** trắng đi ngang (đặc sản đầu đông Hà Nội). Cây bàng chỉ còn vài
chiếc lá đỏ, hoa giấy thưa thớt, dây đèn nháy quấn mái trạm. Mèo cuộn tròn ngủ. Xe máy chở **cành đào** đi ngang (Tết đang về). Đêm **giao thừa**: pháo hoa nổ trên
mái nhà, người dừng xe đứng xem → pháo tắt, trời hửng → hoà về khung đầu tiên của mùa xuân = vòng lặp.

**Xuyên suốt:** xe buýt dừng trạm theo nhịp ~40 s, ô tô + xe máy hai chiều (làn xa chạy phải→trái, làn gần
trái→phải), người đi bộ, chim bay ngang trời / đậu dây điện, tiêu đề mùa bằng chữ pixel ở góc ("XUÂN",
"HẠ", "THU", "ĐÔNG"). Chuyển mùa: hoà tan kiểu dither pixel 3–4 s, nền giữ nguyên.

## 3. Công nghệ
| Việc | Công cụ | Lý do |
|---|---|---|
| Vẽ assets | Python + Pillow, sprite ASCII/procedural (`tools/px.py`) | Mỗi lớp tách riêng, khoá bảng màu, giống hệt nhau giữa 4 mùa — model ảnh AI không làm được cảnh cố định nhiều lớp như vậy |
| Dựng video | **Remotion** (+ Remotion agent skills) | Render theo frame, quyết định được (deterministic), React → dễ chia việc cho subagent |
| Vẽ khung hình | 1 `<canvas>` 480×270 mỗi frame, CSS `image-rendering: pixelated` ×4 | Pixel-perfect, nhanh; hạt mưa/lá/cánh hoa dùng random có seed |
| Ánh sáng / mùa | Lớp phủ multiply/screen theo mùa + giờ, lớp đèn riêng cho ban đêm | Đổi ngày → đêm không cần vẽ lại assets |
| Âm thanh | Remotion `<Audio>` + **FFmpeg** loudnorm −14 LUFS | Nhạc lofi + SFX (mưa, ve, xe máy, phanh buýt, trống lân, mèo kêu, than nổ lách tách) |
| Xuất bản | FFmpeg: MP4 H.264 1080p/4K, bản loop 1h | |

Không dùng: GSAP/Anime/Motion (Remotion đã điều khiển theo frame), Three.js/R3F (không có 3D), Rive/Lottie,
Satori/SVGO (không có vector), Howler/Mediabunny (âm thanh đã nằm trong Remotion).
Lưu ý license: Remotion miễn phí cho cá nhân / công ty ≤3 người, đông hơn cần mua company license.

## 4. Các giai đoạn
1. **Assets + phối cảnh** — 5 subagent Sonnet vẽ song song (env, shelter, vehicles, characters, seasonal), mình
   ghép 4 khung tĩnh từng mùa + bảng sprite → **anh duyệt** ← *đang ở đây*
2. **Engine Remotion** — 1 subagent: dự án Remotion, nạp sprite strip + JSON, renderer canvas, hệ lớp theo `Z_ORDER`,
   DSL timeline (actor đi từ x→x, trạng thái theo thời gian), hạt thời tiết có seed, grading ngày/đêm.
3. **Dựng 4 mùa** — 4 subagent song song, mỗi mùa 1 file timeline dùng API của engine; mình render still ở các mốc
   để soát, chỉnh nhịp.
4. **Âm thanh + render + QA** — mix SFX theo timeline, loudnorm, render 1080p + 4K, kiểm loop liền mạch, bản 1h.
