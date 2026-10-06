#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_images_docx.py — собирает .docx со ВСЕМИ картинками новеллы.

Состав: фоны (20), спрайты персонажей (18), CG (13), служебный арт меню
и карточек (4). Подписи берутся из комментариев images.rpy (там же, где
их читает движок), для gui-арта — из таблицы ниже.

Фоны/CG/menu-арт вставляются ужатыми до 1400 px по ширине (JPEG q82),
чтобы документ весил десятки мегабайт, а не сотни; спрайты вставляются
как есть (они небольшие и с альфа-каналом).

Запуск: python3 tools/export_images_docx.py [OUT]
"""
import os
import re
import sys

from PIL import Image
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
GAME = os.path.join(ROOT, "renpy_project", "game")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, "Лето_которого_не_было_картинки.docx")
PREP = "/tmp/imgprep"
os.makedirs(PREP, exist_ok=True)

GUI_ART = [
    ("gui/main_menu.png", "gui / main_menu", "Арт главного меню (титул)"),
    ("gui/game_menu.png", "gui / game_menu", "Фон внутренних меню (сохранение, настройки, история)"),
    ("gui/card_bg.jpg", "gui / card_bg", "Фон титульных карточек дня и концовок"),
    ("gui/box_frame.png", "gui / box_frame", "Рамка диалогового окна"),
]


def prep(path, max_w=1400, quality=82):
    """Ужатая копия для вставки; возвращает путь и итоговый размер."""
    src = os.path.join(GAME, path)
    im = Image.open(src)
    w, h = im.size
    if w > max_w:
        im = im.resize((max_w, int(h * max_w / w)), Image.LANCZOS)
    base = os.path.basename(path)
    if im.mode in ("RGBA", "LA", "P"):
        out = os.path.join(PREP, base + ".png")
        im.convert("RGBA").save(out, optimize=True)
    else:
        out = os.path.join(PREP, base + ".jpg")
        im.convert("RGB").save(out, quality=quality, optimize=True)
    return out, im.size


# --- парсим images.rpy: tag, файл, комментарий-описание ---
entries = []
img_re = re.compile(r'^image\s+(?P<tag>[\w ]+?)\s*=\s*"(?P<file>images/[^"]+)"\s*(?:#\s*(?P<note>.*))?$')
for line in open(os.path.join(GAME, "images.rpy"), encoding="utf-8"):
    m = img_re.match(line.rstrip())
    if m:
        entries.append({
            "tag": " ".join(m.group("tag").split()),
            "file": m.group("file"),
            "note": (m.group("note") or "").strip(),
        })

bgs = [e for e in entries if e["tag"].startswith("bg ")]
cgs = [e for e in entries if e["tag"].startswith("cg_")]
sprites = [e for e in entries if e not in bgs and e not in cgs]

doc = Document()

# альбомная ориентация — фоны 16:9
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = sec.page_height, sec.page_width

st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(11)

t = doc.add_heading("«Лето, которого не было»", level=0)
p = doc.add_paragraph("Полный комплект изображений визуальной новеллы: "
                      "фоны, спрайты персонажей, CG-иллюстрации и служебный арт.")
p.add_run("\nВерсия 1.2.2 · фонов: %d · спрайтов: %d · CG: %d · служебных: %d"
          % (len(bgs), len(sprites), len(cgs), len(GUI_ART))).italic = True
doc.add_paragraph("Подписи совпадают с именами образов в игре "
                  "(images.rpy) — по ним к картинкам обращается сценарий.")


def caption(tag, note, path, size):
    c = doc.add_paragraph()
    r = c.add_run("%s" % tag)
    r.bold = True
    r.font.size = Pt(10)
    r2 = c.add_run("  —  %s" % note if note else "")
    r2.font.size = Pt(10)
    r2.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    r3 = c.add_run("\n%s · %d×%d px" % (path, size[0], size[1]))
    r3.font.size = Pt(8)
    r3.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    c.paragraph_format.space_after = Pt(14)


def add_full(e):
    out, size = prep(e["file"])
    doc.add_picture(out, width=Inches(8.6))
    doc.paragraphs[-1].alignment = 1
    caption(e["tag"], e["note"], e["file"], size)


# ---------------------------------------------------------------- фоны
doc.add_page_break()
doc.add_heading("1. Фоны локаций (%d)" % len(bgs), level=1)
for e in bgs:
    add_full(e)

# ---------------------------------------------------------------- CG
doc.add_page_break()
doc.add_heading("2. CG-иллюстрации (%d)" % len(cgs), level=1)
for e in cgs:
    add_full(e)

# ---------------------------------------------------------------- спрайты
doc.add_page_break()
doc.add_heading("3. Спрайты персонажей (%d)" % len(sprites), level=1)
doc.add_paragraph("Прозрачный фон (альфа-канал): в игре спрайты рисуются "
                  "поверх фона локации. В документе прозрачность показана "
                  "белым полем.")
cur = None
for e in sprites:
    who = e["tag"].split()[0]
    if who != cur:
        cur = who
        doc.add_heading({"lena": "Лена", "vera": "Вера", "zoya": "Зоя"}.get(who, who),
                        level=2)
    out, size = prep(e["file"], max_w=4000)   # спрайты не ужимаем
    doc.add_picture(out, height=Inches(3.4))
    caption(e["tag"], e["note"], e["file"], size)

# ---------------------------------------------------------------- gui
doc.add_page_break()
doc.add_heading("4. Служебный арт меню и карточек (%d)" % len(GUI_ART), level=1)
for path, tag, note in GUI_ART:
    out, size = prep(path)
    if path.endswith("box_frame.png"):
        doc.add_picture(out, width=Inches(3.0))
    else:
        doc.add_picture(out, width=Inches(8.6))
        doc.paragraphs[-1].alignment = 1
    caption(tag, note, path, size)

doc.save(OUT)
print("Готово: %s (%.1f МБ)" % (os.path.relpath(OUT, ROOT),
                                os.path.getsize(OUT) / 1e6))
print("Фонов: %d · CG: %d · спрайтов: %d · служебных: %d"
      % (len(bgs), len(cgs), len(sprites), len(GUI_ART)))
