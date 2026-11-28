"""올로AI 교재·추가 조립서 PDF 에서 수업 화면용 그림을 만든다 (PyMuPDF·Pillow 필요).

  venv/Scripts/python.exe scripts/build_ollo_assets.py "D:/.../올로AI/교재-조립서" 2     # 끝 숫자는 단계

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
from courses.robot_lessons import ollo_lv1, ollo_lv1_kids, ollo_lv2   # noqa: E402  (낱말 그림 위치)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'robot_lessons_media')
EXT_DIR = 'OLLO_AI_1단계 조립서 예제별'
LEVELS = {
    # pages: 로봇마다 (교재 이론 쪽, 조립서 첫 쪽, 조립서 끝 쪽)
    1: {'book': 'OLLO_AI_Level_1_ver2405_compressed.pdf', 'lessons': ollo_lv1.LESSONS, 'art': ollo_lv1_kids.ART, 'ext': EXT_DIR,
        'pages': [(8 * n, 8 * n + 1, 8 * n + 7) for n in range(1, 13)]},
    2: {'book': 'OLLO_AI_Level_2_ver2410-압축됨.pdf', 'lessons': ollo_lv2.LESSONS, 'art': ollo_lv2.ART, 'ext': None,
        'pages': [(8, 9, 17), (18, 19, 29), (30, 31, 39), (40, 41, 52), (54, 55, 63), (64, 65, 75),
                  (76, 77, 87), (88, 89, 97), (98, 99, 109), (110, 111, 118), (120, 121, 131), (132, 133, 143)]},
}


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


def parts_box_top(cover):
    """부품 목록의 하늘색 테두리가 시작하는 높이 (없으면 쪽의 60%)."""
    w, h = cover.size
    small = cover.convert('RGB').resize((w // 2, h // 2), Image.BOX)
    pixels = small.load()
    for y in range(int(small.height * 0.2), int(small.height * 0.6)):
        blue = sum(1 for x in range(small.width)
                   if pixels[x, y][2] > 200 and pixels[x, y][2] - pixels[x, y][0] > 25)
        if blue > small.width * 0.5:
            return y * 2 - 8
    return int(h * 0.60)


def thumbnail(cover):
    """조립서 첫 쪽에서 완성 로봇 그림만 잘라 낸다 (아래 부품 목록·로봇 이름은 빼고)."""
    w, h = cover.size
    area = cover.crop((int(w * 0.04), int(h * 0.03), int(w * 0.96), parts_box_top(cover)))
    keep = big_shapes(area)
    area = Image.composite(area, Image.new('RGB', area.size, 'white'), keep)
    robot = area.crop(keep.getbbox())
    side = int(max(robot.size) * 1.08)
    canvas = Image.new('RGB', (side, side), 'white')
    canvas.paste(robot, ((side - robot.width) // 2, (side - robot.height) // 2))
    return canvas.resize((480, 480), Image.LANCZOS)


def word_pictures(book, art, lesson, folder):
    """낱말 그림: 교재에서 잘라 내거나(crop), 직접 그린 그림(svg), 완성 로봇(thumb)."""
    for n, (_term, _desc, pic) in enumerate(lesson['words'], 1):
        path = os.path.join(folder, f'word-{n:02d}')
        kind, _, rest = pic.partition(':')
        if kind == 'svg':
            with open(path + '.svg', 'w', encoding='utf-8') as f:
                f.write(art[rest])
        elif kind == 'thumb':
            shutil.copy(os.path.join(folder, 'thumb.jpg'), path + '.jpg')
        else:
            number, box = rest.split(':')
            page = render(book, int(number), 1600)   # 좌표는 쪽 너비 800 기준
            save(page.crop([int(v) * 2 for v in box.split(',')]), path + '.jpg')


def main(pdf_dir, level):
    conf = LEVELS[level]
    book = fitz.open(os.path.join(pdf_dir, conf['book']))
    code_dir = os.path.join(ROOT, 'courses', 'robot_lessons', f'ollo_lv{level}_code')
    ext_files = []
    if conf['ext']:
        ext_files = sorted(glob.glob(os.path.join(pdf_dir, conf['ext'], '*.pdf')),
                           key=lambda f: int(re.match(r'\d+-(\d+)', os.path.basename(f)).group(1)))
        assert len(ext_files) == 12, ext_files
    guide = render(book, 5, 1100)   # 리벳툴·전지·실행 방법
    for n, lesson in enumerate(conf['lessons'], 1):
        folder = os.path.join(OUT, lesson['key'])
        shutil.rmtree(folder, ignore_errors=True)
        _theory, first, last = conf['pages'][n - 1]
        for i, number in enumerate(range(first, last + 1), 1):
            page = render(book, number, 1100)
            save(page, os.path.join(folder, f'build-{i:02d}.jpg'))
            if i == 1:
                save(thumbnail(page), os.path.join(folder, 'thumb.jpg'))
        if ext_files:
            ext = fitz.open(ext_files[n - 1])
            for i in range(1, ext.page_count + 1):
                save(render(ext, i, 1100), os.path.join(folder, f'ext-{i:02d}.jpg'))
        save(guide, os.path.join(folder, 'guide.jpg'))
        shutil.copy(os.path.join(code_dir, f'code{n:02d}.svg'), os.path.join(folder, 'code.svg'))
        if lesson['code'].get('drive'):
            shutil.copy(os.path.join(code_dir, 'code-drive.svg'), os.path.join(folder, 'code-drive.svg'))
        word_pictures(book, conf['art'], lesson, folder)
        print(folder, 'build pages', last - first + 1)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
