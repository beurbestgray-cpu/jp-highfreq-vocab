#!/usr/bin/env python3
"""生成 A4 日语高频词速查 PDF"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "words.csv"
OUT_DIR = ROOT / "output"
OUT_PDF = OUT_DIR / "jp_highfreq_vocab.pdf"

# STSong 对简体+假名覆盖最好；TTF 日文字体缺不少简体字
CID_CANDIDATES = ("STSong-Light", "HeiseiKakuGo-W5", "HeiseiMin-W3")
TTF_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/sand-box/google/BIZ UDPMincho/BIZUDPMincho-Regular.ttf",
    "/usr/share/fonts/truetype/sand-box/google/Sawarabi Mincho/SawarabiMincho-Regular.ttf",
    "/usr/share/fonts/truetype/sand-box/google/DotGothic16/DotGothic16-Regular.ttf",
]


def register_fonts() -> tuple[str, str]:
    for cid in CID_CANDIDATES:
        try:
            pdfmetrics.registerFont(UnicodeCIDFont(cid))
            print(f"字体(CID)：{cid}")
            return cid, cid
        except Exception as e:
            print(f"跳过 CID {cid}: {e}", file=sys.stderr)

    for path in TTF_CANDIDATES:
        p = Path(path)
        if not p.exists():
            continue
        try:
            if p.suffix.lower() == ".ttc":
                pdfmetrics.registerFont(TTFont("CJK", str(p), subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont("CJK", str(p)))
            print(f"字体(TTF)：{p}")
            return "CJK", "CJK"
        except Exception as e:
            print(f"跳过 {p}: {e}", file=sys.stderr)

    print("警告：无 CJK 字体，中文可能方框。", file=sys.stderr)
    return "Helvetica", "Helvetica"


def load_words() -> list[dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    font, font_bold = register_fonts()
    words = load_words()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="日语高频词速查",
        author="jp-highfreq-vocab",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCJK",
        parent=styles["Title"],
        fontName=font_bold,
        fontSize=18,
        leading=24,
        spaceAfter=4,
        textColor=colors.HexColor("#1a1a1a"),
    )
    sub_style = ParagraphStyle(
        "SubCJK",
        parent=styles["Normal"],
        fontName=font,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#555555"),
        spaceAfter=10,
    )
    cell = ParagraphStyle(
        "CellCJK",
        parent=styles["Normal"],
        fontName=font,
        fontSize=8,
        leading=11,
    )
    cell_bold = ParagraphStyle(
        "CellBoldCJK",
        parent=styles["Normal"],
        fontName=font_bold,
        fontSize=8,
        leading=11,
    )

    story = []
    story.append(Paragraph("日语高频词速查（N5 常用）", title_style))
    story.append(
        Paragraph(
            f"共 {len(words)} 词 · 汉字 / 假名 / 罗马音 / 中文 / 例句 · 用 study.py quiz 刷题",
            sub_style,
        )
    )

    header = [
        Paragraph("<b>#</b>", cell_bold),
        Paragraph("<b>汉字</b>", cell_bold),
        Paragraph("<b>假名</b>", cell_bold),
        Paragraph("<b>罗马音</b>", cell_bold),
        Paragraph("<b>中文</b>", cell_bold),
        Paragraph("<b>例句</b>", cell_bold),
    ]
    data = [header]

    for i, w in enumerate(words, 1):
        ex = w.get("example_ja") or ""
        if w.get("example_zh"):
            ex = (
                f"{ex}<br/><font color='#666666'>{w['example_zh']}</font>"
                if ex
                else w["example_zh"]
            )
        data.append(
            [
                Paragraph(str(i), cell),
                Paragraph(w.get("kanji") or "", cell_bold),
                Paragraph(w.get("kana") or "", cell),
                Paragraph(w.get("romaji") or "", cell),
                Paragraph(w.get("meaning_zh") or "", cell),
                Paragraph(ex, cell),
            ]
        )

    col_widths = [10 * mm, 22 * mm, 28 * mm, 28 * mm, 28 * mm, 66 * mm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f7f9fb")],
                ),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph(
            "提示：把 words.csv 改了再跑 python make_pdf.py 即可更新本表。",
            sub_style,
        )
    )

    doc.build(story)
    print(f"已生成：{OUT_PDF}")


if __name__ == "__main__":
    main()
