"""AICE Future 3급 대비 모의평가 2~10차 시험 데이터를 Item.exam_data에 저장한다.

사용: python manage.py shell -c "exec(open('scripts/seed_aice_future_exams_2_10.py', encoding='utf-8').read())"

- 문항 이미지는 media/exam/aice_future_{N}/q{1..8}.jpg (교재 스캔에서 잘라낸 문제 전체),
  정답 및 해설 이미지는 g1.jpg, g2.jpg
- 코디니 문제 파일/정답 파일은 media/exam_gen/item{ID}/q{2..8}.gen, a{2..8}.gen
- 문항 1은 이론(객관식), 2~5는 실습 A형(10점), 6~7은 실습 B형(15점), 8은 프로젝트형(20점)
- 문항 1 정답 번호는 교재 정답 및 해설 기준
"""
import json
from courses.models import Item

# 차수 -> 문항 1 정답 번호
Q1_ANSWERS = {2: 4, 3: 3, 4: 2, 5: 3, 6: 4, 7: 3, 8: 2, 9: 4, 10: 2}
FIRST_ITEM_ID = 1177  # 1차 = 1178 → N차 = 1177 + N


def build(n):
    img = '/media/exam/aice_future_%d/' % n
    qs = [{'no': 1, 'kind': 'mcq', 'points': 10, 'label': '이론', 'text': '',
           'image': img + 'q1.jpg', 'choices': ['', '', '', ''], 'answer': Q1_ANSWERS[n], 'explain': ''}]
    for no in range(2, 9):
        if no <= 5:
            kind, pts, label = 'fill', 10, '실습 A형'
        elif no <= 7:
            kind, pts, label = 'build', 15, '실습 B형'
        else:
            kind, pts, label = 'build', 20, '프로젝트형'
        qs.append({'no': no, 'kind': kind, 'points': pts, 'label': label, 'text': '',
                   'image': img + 'q%d.jpg' % no, 'choices': [], 'answer': None, 'explain': '',
                   'answer_image': ''})
    return {'title': '[%d회] 3급' % n, 'minutes': 50, 'questions': qs,
            'answer_pages': [img + 'g1.jpg', img + 'g2.jpg']}


for n in range(2, 11):
    it = Item.objects.get(id=FIRST_ITEM_ID + n)
    it.exam_data = json.dumps(build(n), ensure_ascii=False)
    it.requires_coding = True
    it.save(update_fields=['exam_data', 'requires_coding'])
    print('saved', n, it.id, it.title)

# 1차에도 교재 정답 및 해설 이미지 추가
it1 = Item.objects.get(id=1178)
d1 = json.loads(it1.exam_data)
d1['answer_pages'] = ['/media/exam/aice_future_1/g1.jpg', '/media/exam/aice_future_1/g2.jpg']
it1.exam_data = json.dumps(d1, ensure_ascii=False)
it1.save(update_fields=['exam_data'])
print('updated 1차 guide pages')
