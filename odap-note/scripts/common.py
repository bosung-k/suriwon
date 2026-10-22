# -*- coding: utf-8 -*-
"""오답노트 도구 공통: 경로 설정(config.json) 읽기/자동 탐색."""
import json
import os
import string
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ACADEMY_DIR = "01.수리원수학학원"
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".claude", "오답노트_config.json")

# 학원 루트 기준 상대 경로 (드라이브 위치만 PC마다 다름)
REL = {
    "note_root": os.path.join("05. 강사별 폴더", "00. 오답노트"),
    "template": os.path.join("05. 강사별 폴더", "00. 오답노트", "오답노트 양식.hwp"),
    "elem": "100. 초등부",
    "middle": "200. 중등부",
    "high": "300. 고등부",
}


def _candidates():
    """Google Drive 안에서 학원 폴더가 있을 만한 위치들."""
    for letter in string.ascii_uppercase:
        root = f"{letter}:\\"
        if not os.path.exists(root):
            continue
        # 공유 드라이브 바로가기 / 내 드라이브 / 공유 드라이브
        sc = os.path.join(root, ".shortcut-targets-by-id")
        if os.path.isdir(sc):
            for d in os.listdir(sc):
                yield os.path.join(sc, d, ACADEMY_DIR)
        for sub in ("내 드라이브", "My Drive", "공유 드라이브", "Shared drives"):
            base = os.path.join(root, sub)
            if os.path.isdir(base):
                yield os.path.join(base, ACADEMY_DIR)
                try:
                    for d in os.listdir(base):
                        yield os.path.join(base, d, ACADEMY_DIR)
                except OSError:
                    pass
        yield os.path.join(root, ACADEMY_DIR)


def find_academy_root():
    for c in _candidates():
        if os.path.isfile(os.path.join(c, REL["template"])):
            return c
    return None


def load_config(required=True):
    cfg = {}
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
    root = cfg.get("academy_root")
    if not root or not os.path.isdir(root):
        root = find_academy_root()
        if root:
            cfg["academy_root"] = root
            save_config(cfg)
    if required and not root:
        sys.exit(
            "ERROR: 학원 폴더(01.수리원수학학원)를 찾지 못했습니다. "
            "사용자에게 경로를 물어본 뒤 `python setup_paths.py --root \"<경로>\"`로 지정하세요."
        )
    if root:
        cfg["paths"] = {k: os.path.join(root, v) for k, v in REL.items()}
    return cfg


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    data = {k: v for k, v in cfg.items() if k != "paths"}
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
