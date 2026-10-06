#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_release_zip.py — сборка ОДНОГО компактного zip-архива игры
«Лето, которого не было» (релиз v1.2 «single-file»).

Зачем: полный пак v1.1 весил 64 МБ и не скачивался одним файлом.
Здесь тот же контент, но ассеты пережаты в форматы, которые Ren'Py 8
поддерживает официально (см. renpy.org/doc/html/displayables.html —
«AVIF WEBP PNG JPG», renpy.org/doc/html/audio.html — «Opus, Ogg Vorbis, …»):

  * фоны и CG      : JPEG q90  -> WebP q76   (1920x1080, то же изображение)
  * спрайты        : PNG       -> WebP q86   (с альфа-каналом)
  * меню-арт/GUI   : PNG/JPEG  -> WebP q85
  * музыка         : Vorbis ~120k -> Opus ~55k (петли остаются бесшовными:
                     длительность и RMS краёв проверяются после кодирования)
  * SFX/амбиенты   : Vorbis -> Opus mono
  * шрифты PT      : оставляем только 4 используемых и сабсетим их
                     (кириллица + латиница + пунктуация)

Все ссылки в .rpy переписываются автоматически, затем прогоняется
tools/validate_project.py по собранной копии — релиз не собирается,
если хоть одна ссылка битая.

Использование:
    python3 tools/make_release_zip.py [--preset balanced|lite] [--out PATH]
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
SRC_GAME = os.path.join(PROJ, "renpy_project", "game")
MASTERS = "/home/user/work_audio"          # исходные PNG 2048x2048 (до кропа 16:9)
STAGE = "/home/user/pack_stage"
TOOLS = os.path.join(PROJ, "tools")

PRESETS = {
    # (webp фонов, webp спрайтов, webp gui, opus музыка, opus sfx, сторона фона)
    "balanced": dict(bg=76, sprite=86, gui=85, music=40000, sfx=28000, size=1920),
    "lite":     dict(bg=70, sprite=80, gui=80, music=32000, sfx=24000, size=1600),
    "max":      dict(bg=85, sprite=92, gui=90, music=64000, sfx=40000, size=1920),
}

SKIP_DIRS = {"cache", "saves", "__pycache__"}
SKIP_FILES = {"prepare_result.txt"}


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# копирование
# ---------------------------------------------------------------------------
def copy_tree(src, dst):
    n = 0
    for root, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = os.path.relpath(root, src)
        out = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(out, exist_ok=True)
        for fn in filenames:
            if fn in SKIP_FILES or fn.endswith(".rpyc") or fn.endswith(".pyc"):
                continue
            shutil.copyfile(os.path.join(root, fn), os.path.join(out, fn))
            n += 1
    return n


# ---------------------------------------------------------------------------
# изображения
# ---------------------------------------------------------------------------
def crop_master(path, side, yoff=0.5):
    """Повторяет work_audio/fix_bg.py: кроп 16:9 -> side x side*9/16 -> unsharp."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    ch = int(w * 9 / 16)
    y0 = int((h - ch) * yoff)
    im = im.crop((0, y0, w, y0 + ch)).resize((side, int(side * 9 / 16)), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))


def diff(a, b):
    import numpy as np
    a = np.asarray(a.convert("RGB"), dtype=np.int16)
    b = np.asarray(b.convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        return 999.0
    return float(abs(a - b).mean())


def save_webp(im, dst, q, method=4):
    im.save(dst, quality=q, method=method)
    return os.path.getsize(dst)


def optimize_images(game, P):
    side = P["size"]
    img = os.path.join(game, "images")
    total_before = total_after = 0
    from_master = 0

    for fn in sorted(os.listdir(img)):
        src = os.path.join(img, fn)
        stem, ext = os.path.splitext(fn)
        ext = ext.lower()
        if ext not in (".jpg", ".jpeg", ".png"):
            continue
        total_before += os.path.getsize(src)
        dst = os.path.join(img, stem + ".webp")

        if ext in (".jpg", ".jpeg"):
            # фон/CG: пробуем взять бесcпорный мастер (PNG до jpeg-сжатия)
            master = os.path.join(MASTERS, stem + ".png")
            base = Image.open(src).convert("RGB")
            if os.path.exists(master):
                m = crop_master(master, base.size[0])
                if diff(m, base) < 3.0:      # мастер совпадает с отгруженным кадром
                    base = m
                    from_master += 1
            if side != 1920:
                base = base.resize((side, int(side * 9 / 16)), Image.LANCZOS)
            save_webp(base, dst, P["bg"])
        else:
            im = Image.open(src)
            if im.mode != "RGBA":
                im = im.convert("RGBA")
            if side != 1920:
                k = side / 1920.0
                im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))),
                               Image.LANCZOS)
            save_webp(im, dst, P["sprite"])

        total_after += os.path.getsize(dst)
        os.remove(src)
        log(f"  images/{fn} -> {stem}.webp  "
            f"{os.path.getsize(dst)/1024:.0f} КБ")

    # GUI
    gui = os.path.join(game, "gui")
    for fn, q in (("main_menu.png", P["gui"]), ("game_menu.png", P["gui"])):
        p = os.path.join(gui, fn)
        if os.path.exists(p):
            total_before += os.path.getsize(p)
            im = Image.open(p).convert("RGB")
            if side != 1920:
                im = im.resize((side, int(side * 9 / 16)), Image.LANCZOS)
            dst = os.path.join(gui, os.path.splitext(fn)[0] + ".webp")
            save_webp(im, dst, q)
            total_after += os.path.getsize(dst)
            os.remove(p)
            log(f"  gui/{fn} -> {os.path.basename(dst)}  {os.path.getsize(dst)/1024:.0f} КБ")
    p = os.path.join(gui, "card_bg.jpg")
    if os.path.exists(p):
        total_before += os.path.getsize(p)
        im = Image.open(p).convert("RGB")
        dst = os.path.join(gui, "card_bg.webp")
        save_webp(im, dst, P["gui"])
        total_after += os.path.getsize(dst)
        os.remove(p)
        log(f"  gui/card_bg.jpg -> card_bg.webp  {os.path.getsize(dst)/1024:.0f} КБ")

    log(f"[img] {total_before/1048576:.1f} МБ -> {total_after/1048576:.1f} МБ "
        f"(мастер-PNG использован для {from_master} кадров)")
    return total_before, total_after


# ---------------------------------------------------------------------------
# шрифты: оставить только используемые и отсабсетить
# ---------------------------------------------------------------------------
USED_FONTS = {"PTSans-Regular.ttf", "PTSans-Bold.ttf", "PTSans-Italic.ttf",
              "PTSerif-BoldItalic.ttf"}
KEEP_RANGES = [(0x20, 0x7E), (0xA0, 0xFF), (0x300, 0x36F), (0x400, 0x52F),
               (0x2000, 0x206F), (0x20A0, 0x20CF), (0x2116, 0x2116),
               (0x2122, 0x2122), (0x2190, 0x21FF), (0x25A0, 0x27BF),
               (0xFB00, 0xFB06), (0xFEFF, 0xFEFF)]


def subset_fonts(game, extra_text=""):
    from fontTools import subset
    fonts = os.path.join(game, "gui", "fonts")
    unicodes = ",".join(f"U+{a:04X}-{b:04X}" if a != b else f"U+{a:04X}"
                        for a, b in KEEP_RANGES)
    before = after = 0
    for fn in sorted(os.listdir(fonts)):
        p = os.path.join(fonts, fn)
        before += os.path.getsize(p)
        if fn not in USED_FONTS:
            os.remove(p)
            log(f"  fonts/{fn} — удалён (не используется)")
            continue
        opts = subset.Options()
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        opts.recalc_bounds = True
        opts.ignore_missing_glyphs = True
        opts.drop_tables = []
        f = subset.load_font(p, opts)
        s = subset.Subsetter(opts)
        s.populate(unicodes=[c for a, b in KEEP_RANGES for c in range(a, b + 1)],
                   text=extra_text)
        s.subset(f)
        subset.save_font(f, p + ".tmp", opts)
        f.close()
        os.replace(p + ".tmp", p)
        after += os.path.getsize(p)
        log(f"  fonts/{fn}: сабсет -> {os.path.getsize(p)/1024:.0f} КБ")
    log(f"[fonts] {before/1048576:.2f} МБ -> {after/1048576:.2f} МБ")


# ---------------------------------------------------------------------------
# звук
# ---------------------------------------------------------------------------
def optimize_audio(game, P):
    before = after = 0
    mus = os.path.join(game, "audio")
    sfx = os.path.join(mus, "sfx")
    for d, mono, br in ((mus, False, P["music"]), (sfx, True, P["sfx"])):
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".ogg"):
                continue
            p = os.path.join(d, fn)
            before += os.path.getsize(p)
            tmp = p + ".tmp.ogg"
            cmd = [sys.executable, os.path.join(TOOLS, "reencode_opus.py"),
                   p, tmp, "--bitrate", str(br), "--quiet"]
            if mono:
                cmd.append("--mono")
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                raise SystemExit(f"ошибка пережатия {fn}: {r.stdout}\n{r.stderr}")
            os.replace(tmp, p)
            after += os.path.getsize(p)
            log(f"  audio/{os.path.relpath(p, mus)}: {os.path.getsize(p)/1024:.0f} КБ")
    log(f"[audio] {before/1048576:.1f} МБ -> {after/1048576:.1f} МБ (Opus)")


# ---------------------------------------------------------------------------
# правка ссылок в .rpy
# ---------------------------------------------------------------------------
def patch_refs(game):
    import re
    changed = 0

    def repl(m):
        old = m.group(0)
        new = m.group(1) + '.webp"'
        # переписываем ссылку ТОЛЬКО если .webp действительно создан
        # (gui/box_frame.png остаётся PNG — это Frame() 96x96)
        if os.path.exists(os.path.join(game, m.group(1) + ".webp")):
            return new
        return old

    for root, dirnames, filenames in os.walk(game):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".rpy"):
                continue
            p = os.path.join(root, fn)
            s = open(p, encoding="utf-8").read()
            o = s
            s = re.sub(r'((?:images|gui)/[A-Za-z0-9_\-]+)\.(?:png|jpg|jpeg)"', repl, s)
            if s != o:
                open(p, "w", encoding="utf-8").write(s)
                changed += 1
                log(f"  refs: {os.path.relpath(p, game)}")
    log(f"[refs] обновлено файлов: {changed}")


def check_refs(game):
    """Финальная сверка: каждый упомянутый в .rpy ассет существует."""
    import re
    bad = []
    for root, dirnames, filenames in os.walk(game):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".rpy"):
                continue
            p = os.path.join(root, fn)
            for i, line in enumerate(open(p, encoding="utf-8"), 1):
                if line.strip().startswith("#"):
                    continue
                for m in re.finditer(r'"((?:images|gui|audio)/[A-Za-z0-9_\-./]+\.(?:webp|png|jpg|jpeg|ogg|ttf))"', line):
                    if not os.path.exists(os.path.join(game, m.group(1))):
                        bad.append(f"{os.path.relpath(p, game)}:{i} {m.group(1)}")
    if bad:
        raise SystemExit("БИТЫЕ ССЫЛКИ:\n" + "\n".join(bad))
    log("[refs] все ссылки на ассеты валидны")


# ---------------------------------------------------------------------------
def make_zip(root, out):
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames.sort()
            for fn in sorted(filenames):
                p = os.path.join(dirpath, fn)
                z.write(p, os.path.relpath(p, os.path.dirname(root)))
    size = os.path.getsize(out)
    with zipfile.ZipFile(out) as z:
        bad = z.testzip()
        cnt = len(z.namelist())
    log(f"\n=== ГОТОВО: {out}")
    log(f"    {size/1048576:.2f} МБ, {cnt} файлов, CRC {'OK' if bad is None else 'ОШИБКА: '+str(bad)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", default="balanced", choices=list(PRESETS))
    ap.add_argument("--out", default="/home/user/leto_v1.2_one_file.zip")
    ap.add_argument("--name", default="Leto_kotorogo_ne_bylo")
    ap.add_argument("--zip-only", action="store_true",
                    help="не пережимать ассеты заново, только пересобрать zip "
                         "из уже подготовленного /home/user/pack_build")
    a = ap.parse_args()
    P = PRESETS[a.preset]

    if a.zip_only:
        root = os.path.join(STAGE, a.name)
        if not os.path.isdir(os.path.join(root, "game")):
            raise SystemExit("нет готовой сборки в " + root)
        for f in ("README.md",):
            shutil.copyfile(os.path.join(PROJ, f), os.path.join(root, f))
        copy_tree(os.path.join(PROJ, "docs"), os.path.join(root, "docs"))
        shutil.copyfile(os.path.join(PROJ, "dist_pack", "INSTALL.md"),
                        os.path.join(root, "УСТАНОВКА.md"))
        shutil.copyfile(os.path.join(PROJ, "dist_pack", "install.py"),
                        os.path.join(root, "install.py"))
        make_zip(root, a.out)
        return

    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    root = os.path.join(STAGE, a.name)
    os.makedirs(root)

    log(f"=== preset {a.preset}: {P} ===")
    n = copy_tree(SRC_GAME, os.path.join(root, "game"))
    log(f"[copy] game/: {n} файлов")
    for d in ("docs", "tools"):
        copy_tree(os.path.join(PROJ, d), os.path.join(root, d))
    for f in ("README.md",):
        if os.path.exists(os.path.join(PROJ, f)):
            shutil.copyfile(os.path.join(PROJ, f), os.path.join(root, f))
    for f in ("install.py", "УСТАНОВКА.md"):
        src = os.path.join(PROJ, "dist_pack", f if f != "УСТАНОВКА.md" else "INSTALL.md")
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(root, f))

    game = os.path.join(root, "game")
    optimize_images(game, P)
    subset_fonts(game)
    optimize_audio(game, P)
    patch_refs(game)
    check_refs(game)

    # валидация проекта по собранной копии
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "validate_project.py"), game],
                       capture_output=True, text=True)
    log(r.stdout[-3000:])
    if r.returncode != 0:
        log(r.stderr[-2000:])
        raise SystemExit("validate_project.py НЕ ПРОШЁЛ — архив не собираем")

    # zip
    make_zip(root, a.out)


if __name__ == "__main__":
    main()
