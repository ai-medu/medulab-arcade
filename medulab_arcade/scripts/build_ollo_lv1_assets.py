"""올로AI 1단계 교재·추가 조립서 PDF 에서 수업 화면용 그림을 만든다 (PyMuPDF·Pillow 필요).

  venv/Scripts/python.exe scripts/build_ollo_lv1_assets.py "D:/.../올로AI/교재-조립서"

결과는 robot_lessons_media/<수업키>/ 에 생긴다. 교재는 저작물이므로 저장소에 올리지 않고
서버의 같은 폴더로 따로 복사한다 (로그인한 회원에게만 보여 준다).
"""
import glob
import os
import re
import shutil
import sys

import fitz
from PIL import Image, ImageChops, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from courses.robot_lessons.ollo_lv1 import LESSONS   # noqa: E402  (낱말 그림 위치)
from courses.robot_lessons.ollo_lv1_kids import ART   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'robot_lessons_media')
CODE = os.path.join(ROOT, 'courses', 'robot_lessons', 'ollo_lv1_code')
BOOK = 'OLLO_AI_Level_1_ver2405_compressed.pdf'
EXT_DIR = 'OLLO_AI_1단계 조립서 예제별'


def render(doc, number, width):
    page = doc[number - 1]
    zoom = width / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def save(image, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image.save(path, quality=82, optimize=True, progressive=True)


def big_shapes(area):
    """흰 바탕에서 큰 그림 덩어리만 남기는 마스크 (이름 글자·부품 목록 테두리는 작거나 속이 비어서 빠진다)."""
    diff = ImageChops.difference(area, Image.new('RGB', area.size, 'white')).convert('L').point(lambda v: 255 if v > 14 else 0)
    small_w = 300
    small = diff.resize((small_w, round(area.height * small_w / area.width)), Image.BOX).point(lambda v: 255 if v > 40 else 0)
    w, h = small.size
    pixels = small.load()
    seen, parts = set(), []
    for start in ((x, y) for y in range(h) for x in range(w)):
        if start in seen or not pixels[start]:
            continue
        seen.add(start)
        stack, part = [start], []
        while stack:
            x, y = stack.pop()
            part.append((x, y))
            for nx in (x - 1, x, x + 1):
                for ny in (y - 1, y, y + 1):
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and pixels[nx, ny]:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
        parts.append(part)
    largest = max(len(p) for p in parts)
    mask = Image.new('L', small.size, 0)
    out = mask.load()
    for part in parts:
        xs, ys = [p[0] for p in part], [p[1] for p in part]
        filled = len(part) / ((max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1))
        if len(part) > largest * 0.04 and filled > 0.2:
            for p in part:
                out[p] = 255
    mask = mask.filter(ImageFilter.MaxFilter(5)).resize(area.size, Image.BILINEAR)
    return mask.point(lambda v: 255 if v > 20 else 0)


def thumbnail(cover):
    """조립서 첫 쪽에서 완성 로봇 그림만 잘라 낸다 (아래 부품 목록·로봇 이름은 빼고)."""
    w, h = cover.size
    area = cover.crop((int(w * 0.04), int(h * 0.03), int(w * 0.96), int(h * 0.60)))
    keep = big_shapes(area)
    area = Image.composite(area, Image.new('RGB', area.size, 'white'), keep)
    robot = area.crop(keep.getbbox())
    side = int(max(robot.size) * 1.08)
    canvas = Image.new('RGB', (side, side), 'white')
    canvas.paste(robot, ((side - robot.width) // 2, (side - robot.height) // 2))
    return canvas.resize((480, 480), Image.LANCZOS)


def word_pictures(book, lesson, folder):
    """낱말 그림: 교재에서 잘라 내거나(crop), 직접 그린 그림(svg), 완성 로봇(thumb)."""
    for n, (_term, _desc, pic) in enumerate(lesson['words'], 1):
        path = os.path.join(folder, f'word-{n:02d}')
        kind, _, rest = pic.partition(':')
        if kind == 'svg':
            with open(path + '.svg', 'w', encoding='utf-8') as f:
                f.write(ART[rest])
        elif kind == 'thumb':
            shutil.copy(os.path.join(folder, 'thumb.jpg'), path + '.jpg')
        else:
            number, box = rest.split(':')
            page = render(book, int(number), 1600)   # 좌표는 쪽 너비 800 기준
            save(page.crop([int(v) * 2 for v in box.split(',')]), path + '.jpg')


def main(pdf_dir):
    book = fitz.open(os.path.join(pdf_dir, BOOK))
    ext_files = sorted(glob.glob(os.path.join(pdf_dir, EXT_DIR, '*.pdf')),
                       key=lambda f: int(re.match(r'1-(\d+)', os.path.basename(f)).group(1)))
    assert len(ext_files) == 12, ext_files
    guide = render(book, 5, 1100)   # 리벳툴·전지·실행 방법
    for n in range(1, 13):
        folder = os.path.join(OUT, f'lv1_{n:02d}')
        shutil.rmtree(folder, ignore_errors=True)
        theory = 8 * n              # 이론 1쪽, 이어서 조립서 7쪽
        for i in range(1, 8):
            page = render(book, theory + i, 1100)
            save(page, os.path.join(folder, f'build-{i:02d}.jpg'))
            if i == 1:
                save(thumbnail(page), os.path.join(folder, 'thumb.jpg'))
        ext = fitz.open(ext_files[n - 1])
        for i in range(1, ext.page_count + 1):
            save(render(ext, i, 1100), os.path.join(folder, f'ext-{i:02d}.jpg'))
        save(guide, os.path.join(folder, 'guide.jpg'))
        shutil.copy(os.path.join(CODE, f'code{n:02d}.svg'), os.path.join(folder, 'code.svg'))
        word_pictures(book, LESSONS[n - 1], folder)
        print(folder, 'ext pages', ext.page_count)


if __name__ == '__main__':
    main(sys.argv[1])
