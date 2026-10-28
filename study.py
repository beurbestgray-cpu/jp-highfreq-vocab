#!/usr/bin/env python3
"""日语高频词学习 CLI：quiz / list / add"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "words.csv"
FIELDS = ["kanji", "kana", "romaji", "meaning_zh", "example_ja", "example_zh"]


def load_words(path: Path = CSV_PATH) -> list[dict[str, str]]:
    if not path.exists():
        print(f"找不到词表：{path}", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            cleaned = {k: (row.get(k) or "").strip() for k in FIELDS}
            if cleaned["kana"] or cleaned["kanji"]:
                rows.append(cleaned)
        return rows


def save_words(rows: list[dict[str, str]], path: Path = CSV_PATH) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def display_word(w: dict[str, str]) -> str:
    kanji = w["kanji"]
    kana = w["kana"]
    if kanji and kanji != kana:
        return f"{kanji}（{kana}）"
    return kana or kanji


def normalize_answer(s: str) -> str:
    return (
        s.strip()
        .lower()
        .replace(" ", "")
        .replace("　", "")
        .replace("（", "(")
        .replace("）", ")")
    )


def meaning_ok(user: str, correct: str) -> bool:
    u = normalize_answer(user)
    c = normalize_answer(correct)
    if not u:
        return False
    if u == c:
        return True
    # 允许答对括号外主义，或主义包含用户答案
    main = c.split("(")[0].split("（")[0]
    if u == main or main in u or u in c:
        return True
    return False


def cmd_list(args: argparse.Namespace) -> None:
    words = load_words()
    limit = args.limit
    print(f"共 {len(words)} 个词" + (f"（显示前 {limit}）" if limit else ""))
    print("-" * 60)
    for i, w in enumerate(words[: limit or None], 1):
        ex = f" ｜ {w['example_ja']}" if w.get("example_ja") else ""
        print(
            f"{i:3d}. {display_word(w):20s}  {w['romaji']:16s}  {w['meaning_zh']}{ex}"
        )


def cmd_add(args: argparse.Namespace) -> None:
    words = load_words()
    if args.kanji or args.kana:
        row = {
            "kanji": args.kanji or args.kana or "",
            "kana": args.kana or "",
            "romaji": args.romaji or "",
            "meaning_zh": args.meaning or "",
            "example_ja": args.example_ja or "",
            "example_zh": args.example_zh or "",
        }
        if not row["kana"]:
            print("需要 --kana", file=sys.stderr)
            sys.exit(1)
        if not row["meaning_zh"]:
            print("需要 --meaning", file=sys.stderr)
            sys.exit(1)
    else:
        print("添加新词（直接回车可留空；假名和中文意思必填）")
        kana = input("假名 kana: ").strip()
        if not kana:
            print("已取消。")
            return
        kanji = input(f"汉字 kanji [{kana}]: ").strip() or kana
        romaji = input("罗马音 romaji: ").strip()
        meaning = input("中文意思: ").strip()
        if not meaning:
            print("中文意思必填，已取消。")
            return
        example_ja = input("例句（日）: ").strip()
        example_zh = input("例句（中）: ").strip()
        row = {
            "kanji": kanji,
            "kana": kana,
            "romaji": romaji,
            "meaning_zh": meaning,
            "example_ja": example_ja,
            "example_zh": example_zh,
        }

    # 去重：同假名+同汉字跳过
    for w in words:
        if w["kana"] == row["kana"] and w["kanji"] == row["kanji"]:
            print(f"已存在：{display_word(w)} → {w['meaning_zh']}")
            return
    words.append(row)
    save_words(words)
    print(f"已添加：{display_word(row)} → {row['meaning_zh']}（共 {len(words)} 词）")


def cmd_quiz(args: argparse.Namespace) -> None:
    words = load_words()
    if len(words) < 2:
        print("词太少，请先往 words.csv 加词。", file=sys.stderr)
        sys.exit(1)

    n = min(args.n, len(words))
    pool = words[:]
    random.shuffle(pool)
    selected = pool[:n]

    mode = args.mode
    correct = 0
    print(f"日语高频词测验 · {n} 题 · 模式={mode}" + (" · DEMO" if args.demo else ""))
    print("提示：看假名/汉字，输入中文意思（或选 A/B/C/D）")
    print("-" * 50)

    for i, w in enumerate(selected, 1):
        prompt = display_word(w)
        romaji_hint = f"  [{w['romaji']}]" if args.show_romaji else ""
        print(f"\n{i}/{n}  {prompt}{romaji_hint}")

        if mode == "choice":
            opts = [w["meaning_zh"]]
            distractors = [x["meaning_zh"] for x in words if x is not w]
            random.shuffle(distractors)
            for d in distractors:
                if d not in opts:
                    opts.append(d)
                if len(opts) >= 4:
                    break
            random.shuffle(opts)
            labels = "ABCD"
            for lab, opt in zip(labels, opts):
                print(f"  {lab}. {opt}")
            answer_key = labels[opts.index(w["meaning_zh"])]

            if args.demo:
                user = answer_key
                print(f"  → DEMO 选 {user}")
            else:
                user = input("你的答案 (A-D): ").strip().upper()

            ok = user == answer_key or meaning_ok(user, w["meaning_zh"])
        else:
            if args.demo:
                user = w["meaning_zh"]
                print(f"  → DEMO 答：{user}")
            else:
                user = input("中文意思: ").strip()
            ok = meaning_ok(user, w["meaning_zh"])

        if ok:
            correct += 1
            print("  ✓ 正确")
        else:
            print(f"  ✗ 不对。答案：{w['meaning_zh']} ｜ {w['romaji']}")
        if w.get("example_ja"):
            print(f"  例：{w['example_ja']}（{w.get('example_zh', '')}）")

    pct = round(100 * correct / n) if n else 0
    print("\n" + "=" * 50)
    print(f"得分：{correct}/{n}（{pct}%）")
    if pct == 100:
        print("全对！很稳。")
    elif pct >= 70:
        print("不错，错的再过一遍。")
    else:
        print("再刷一轮，慢慢来。")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="日语高频词学习工具（quiz / list / add）"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("quiz", help="抽认卡测验")
    q.add_argument("-n", type=int, default=10, help="题数（默认 10）")
    q.add_argument(
        "--mode",
        choices=["type", "choice"],
        default="choice",
        help="type=打中文；choice=四选一（默认）",
    )
    q.add_argument("--show-romaji", action="store_true", help="题目显示罗马音")
    q.add_argument(
        "--demo",
        action="store_true",
        help="自动作答演示（不交互，方便测试）",
    )
    q.set_defaults(func=cmd_quiz)

    ls = sub.add_parser("list", help="列出词表")
    ls.add_argument("-n", "--limit", type=int, default=0, help="只显示前 N 个（0=全部）")
    ls.set_defaults(func=cmd_list)

    ad = sub.add_parser("add", help="添加单词")
    ad.add_argument("--kanji", default="", help="汉字")
    ad.add_argument("--kana", default="", help="假名")
    ad.add_argument("--romaji", default="", help="罗马音")
    ad.add_argument("--meaning", default="", help="中文意思")
    ad.add_argument("--example-ja", default="", dest="example_ja")
    ad.add_argument("--example-zh", default="", dest="example_zh")
    ad.set_defaults(func=cmd_add)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
