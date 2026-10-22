# -*- coding: utf-8 -*-
"""경로 확인/지정.
  python setup_paths.py              # 자동 탐색 후 결과 출력
  python setup_paths.py --root "D:\\...\\01.수리원수학학원"   # 수동 지정
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_config, save_config, REL, CONFIG_PATH  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--root")
a = ap.parse_args()

if a.root:
    if not os.path.isfile(os.path.join(a.root, REL["template"])):
        sys.exit(f"ERROR: {a.root} 안에 '{REL['template']}'가 없습니다. 경로를 다시 확인하세요.")
    save_config({"academy_root": a.root})

cfg = load_config()
print("config:", CONFIG_PATH)
print("academy_root:", cfg["academy_root"])
for k, p in cfg["paths"].items():
    print(f"  {k:10s} {'OK ' if os.path.exists(p) else 'MISSING'} {p}")
