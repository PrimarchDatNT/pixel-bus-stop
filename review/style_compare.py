"""Build the style-test comparison page (v1 vs render3d vs shade25d) as one self-contained HTML."""
from __future__ import annotations

import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "assets" / "out"
V2 = ROOT / "assets" / "out_v2"
OUT = ROOT / "review" / "style"


def b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def v1_frame(group: str, name: str, i: int = 0, state: str | None = None) -> Image.Image:
    m = json.loads((V1 / group / f"{name}.json").read_text())
    s = Image.open(V1 / group / f"{name}.png").convert("RGBA")
    if state:
        i = m["states"][state][i]
    fw, fh = m["frameW"], m["frameH"]
    return s.crop((i * fw, 0, (i + 1) * fw, fh))


def tight(img: Image.Image) -> Image.Image:
    bb = img.getbbox()
    return img.crop(bb) if bb else img


def track(name: str) -> dict | None:
    d = V2 / name
    if not (d / "styleframe.png").exists():
        return None
    parts = {}
    for k, f in [("bus", "bus_L.png"), ("cat", "cat_sit.png"), ("bloom", "shelter_ha.png")]:
        if (d / f).exists():
            parts[k] = b64(tight(Image.open(d / f).convert("RGBA")))
    return {"frame": b64(Image.open(d / "styleframe.png").convert("RGB")), "parts": parts}


TRACKS = {
    "v1": {"short": "Bản hiện tại", "name": "Bản 1 · pixel phẳng 480×270",
           "how": "Bảng màu chung 45 màu, người cao 28 px, đổ bóng 3–4 tông.",
           "notes": ["Gọn, làm animation nhanh", "Phẳng, ít khối, chưa có độ bóng"]},
    "render3d": {"short": "Hướng 1 · dựng 3D", "name": "Dựng 3D trong Blender rồi ép về pixel",
                 "how": "Mô hình 3D thật, ánh sáng và phản chiếu thật; render nhỏ rồi giảm màu, kẻ viền cho ra pixel.",
                 "notes": ["Xe buýt có la-zăng, kính phản chiếu, khối xe như thật",
                           "Hoa giấy tự nhiên hơn nhưng lấm tấm; mặt mèo chưa đẹp",
                           "Nhà còn phẳng, cửa cuốn có ô màu vô nghĩa",
                           "Xe, nhà, trạm làm nhanh; người và mèo cần dựng khung xương, tốn công"]},
    "shade25d": {"pick": True, "short": "Hướng 2 · vẽ code + ánh sáng", "name": "Pixel vẽ bằng code, tính ánh sáng 3D",
                 "how": "Mỗi vật ghép từ khối cầu, trụ, hộp; code tính ánh sáng, điểm bóng, viền sáng rồi ép về dải màu 8–10 tông.",
                 "notes": ["Xe buýt, ghế nhựa, mèo đã bóng và có khối rõ",
                           "Hoa giấy còn thành khối đặc, mặt đường hơi lấm tấm",
                           "Animation tốn công nhất: mỗi tư thế phải dựng lại từ khối"]},
}


def main() -> None:
    v1 = {
        "frame": b64(Image.open(ROOT / "review" / "stills" / "ha.png").convert("RGB")),
        "parts": {
            "bus": b64(tight(v1_frame("vehicles", "bus_L", 0))),
            "cat": b64(tight(v1_frame("characters", "cat_R", 0, "sit_idle"))),
            "bloom": b64(tight(v1_frame("shelter", "bougainvillea_ha", 0))),
        },
    }
    data = {"v1": v1, "render3d": track("render3d"), "shade25d": track("shade25d")}
    html = (ROOT / "review" / "style_compare.html").read_text()
    tracks = json.loads(json.dumps(TRACKS))
    if not data["render3d"]:
        tracks["render3d"]["notes"] = tracks["render3d"]["notes"] + ["Đang render, chưa có ảnh"]
    ask = ("Hướng 1 đang chạy, có kết quả mình cập nhật trang này. " if not data["render3d"] else "") + \
        "Mình nghiêng về <b>Hướng 2</b>: ra chất sprite vẽ tay bóng bẩy, gọn và dễ đọc hơn, mèo dễ thương hơn. " \
        "Có thể mượn cách dựng 3D của Hướng 1 riêng cho tán hoa giấy và cây bàng. " \
        "<span class=\"rec\">Anh chọn hướng nào, hoặc chỉ ra chỗ nào cần bóng hơn nữa, mình làm lại toàn bộ assets theo hướng đó.</span>"
    html = html.replace("/*DATA*/null", json.dumps(data))
    html = html.replace("<script>\nconst D =", "<script>window.TRACKS = " + json.dumps(tracks, ensure_ascii=False) +
                        "; window.ASK = " + json.dumps(ask, ensure_ascii=False) + ";</script>\n<script>\nconst D =", 1)
    html = "<!doctype html>\n<html lang=\"vi\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n" + html + "\n</html>\n"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(html)
    print("->", OUT / "index.html", {k: bool(v) for k, v in data.items()})


if __name__ == "__main__":
    main()
