# -*- coding: utf-8 -*-
"""오답노트 HWP 생성.

  python build_note.py job.json

job.json 예:
{
  "teacher": "현승T",
  "student_folder": "이시우(세화여중1)",      # 학생 폴더 이름 (없으면 새로 만듦)
  "file_name": "이시우 유형만렙 중1-2 2-1. 기본 도형 261021.hwp",
  "items": [
    {"book": "유형만렙 중1-2", "unit": "2-1. 기본 도형", "page": "157", "num": "29",
     "image": "C:\\...\\crop_157_29.png"},
    ...
  ]
}
- 양식 1쪽 = 문제 2개. 문제 수에 맞게 쪽을 복제한다.
- 이미 같은 이름 파일이 있으면 덮어쓰지 않고 '(2)'를 붙인다.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_config  # noqa: E402

import win32com.client as win32  # noqa: E402

MAX_W_MM = 165   # [문제] 칸 안 그림 최대 너비
MAX_H_MM = 95    # 풀이 공간을 남기기 위한 최대 높이


def open_hwp():
    hwp = win32.Dispatch("HWPFrame.HwpObject")
    # 한글 보안 승인 팝업 방지 모듈 (install.ps1 이 레지스트리에 등록)
    for name in ("FilePathCheckerModuleExample", "FilePathCheckerModule"):
        try:
            if hwp.RegisterModule("FilePathCheckDLL", name):
                break
        except Exception:
            pass
    hwp.XHwpWindows.Item(0).Visible = False
    return hwp


def scan_cells(hwp):
    """표 셀 목록 [(list_id, 'A2'), ...] 을 문서 순서대로."""
    cells = []
    miss = 0
    i = 1
    while miss < 30:
        if hwp.SetPos(i, 0, 0):
            ind = hwp.KeyIndicator()[-1]
            if ind.startswith("(") and ")" in ind:
                cells.append((i, ind[1:ind.index(")")]))
                miss = 0
            else:
                miss += 1
        else:
            miss += 1
        i += 1
    return cells


def slots(cells):
    """문제 칸 묶음: [{'book','unit','page','num','prob'}: list_id]"""
    out, cur = [], {}
    keymap = {"A2": "book", "B2": "unit", "C2": "page", "D2": "num", "A3": "prob",
              "A5": "book", "B5": "unit", "C5": "page", "D5": "num", "A6": "prob"}
    for lid, name in cells:
        k = keymap.get(name)
        if not k:
            continue
        cur[k] = lid
        if k == "prob":
            out.append(cur)
            cur = {}
    return out


def put_text(hwp, lid, text):
    hwp.SetPos(lid, 0, 0)
    hwp.Run("MoveSelListEnd")
    hwp.Run("Delete")
    act = hwp.HAction
    ps = hwp.HParameterSet.HInsertText
    act.GetDefault("InsertText", ps.HSet)
    ps.Text = str(text)
    act.Execute("InsertText", ps.HSet)


def put_image(hwp, lid, path):
    from PIL import Image
    im = Image.open(path)
    dpi = im.info.get("dpi", (200, 200))[0] or 200
    w_mm = im.width / dpi * 25.4
    h_mm = im.height / dpi * 25.4
    s = min(1.0, MAX_W_MM / w_mm, MAX_H_MM / h_mm)
    # 1번째 문단 = "[ 문제 ]", 2번째 문단(빈 줄)에 그림
    if not hwp.SetPos(lid, 1, 0):
        hwp.SetPos(lid, 0, 0)
        hwp.Run("MoveParaEnd")
        hwp.Run("BreakPara")
    ctrl = hwp.InsertPicture(os.path.abspath(path), True, 1,
                             False, False, 0, int(w_mm * s), int(h_mm * s))
    return ctrl


def unique_path(p):
    if not os.path.exists(p):
        return p
    stem, ext = os.path.splitext(p)
    n = 2
    while os.path.exists(f"{stem}({n}){ext}"):
        n += 1
    return f"{stem}({n}){ext}"


def main():
    job = json.load(open(sys.argv[1], encoding="utf-8"))
    cfg = load_config()
    P = cfg["paths"]
    items = job["items"]
    pages = (len(items) + 1) // 2

    out_dir = job.get("out_dir") or os.path.join(P["note_root"], job["teacher"], job["student_folder"])
    os.makedirs(out_dir, exist_ok=True)
    out = unique_path(os.path.join(out_dir, job["file_name"]))

    work = os.path.join(tempfile.mkdtemp(prefix="odap_"), "work.hwp")
    shutil.copy(P["template"], work)

    hwp = open_hwp()
    try:
        hwp.Open(work, "HWP", "forceopen:true")
        for _ in range(pages - 1):
            hwp.Run("MoveDocEnd")
            act, ps = hwp.HAction, hwp.HParameterSet.HInsertFile
            act.GetDefault("InsertFile", ps.HSet)
            ps.filename = P["template"]
            ps.KeepSection = 1
            ps.KeepCharshape = 1
            ps.KeepParashape = 1
            ps.KeepStyle = 1
            act.Execute("InsertFile", ps.HSet)
        sl = slots(scan_cells(hwp))
        if len(sl) < len(items):
            raise RuntimeError(f"칸 부족: {len(sl)} < {len(items)}")
        for it, s in zip(items, sl):
            put_text(hwp, s["book"], it["book"])
            put_text(hwp, s["unit"], it["unit"])
            put_text(hwp, s["page"], it["page"])
            put_text(hwp, s["num"], it["num"])
            if it.get("image"):
                put_image(hwp, s["prob"], it["image"])
        if hwp.PageCount != pages:
            print(f"WARN: 쪽수 {hwp.PageCount} (예상 {pages}) - 결과 PDF로 확인 필요")
        hwp.SaveAs(out, "HWP")
        preview = os.path.splitext(work)[0] + ".pdf"
        hwp.SaveAs(preview, "PDF")
    finally:
        hwp.Clear(1)
        hwp.Quit()
    print("SAVED:", out)
    print("PREVIEW_PDF:", preview)


if __name__ == "__main__":
    main()
