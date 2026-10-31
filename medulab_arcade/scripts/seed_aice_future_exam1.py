"""AICE Future 3급 대비 모의평가 1차 시험 데이터를 Item.exam_data에 저장한다.

사용: python manage.py shell -c "exec(open('scripts/seed_aice_future_exam1.py', encoding='utf-8').read())"
(교재 117쪽~ 1차 모의평가, 정답/해설은 교재 정답 및 해설 기준)
"""
import json
from courses.models import Item

IMG = '/media/exam/aice_future_1/'
CIRCLED = ['①', '②', '③', '④']

data = {
    'title': '[1회] 3급',
    'minutes': 50,
    'questions': [
        {'no': 1, 'kind': 'mcq', 'points': 10, 'label': '이론',
         'text': '다음 중 인공지능 기술을 활용한 기능이 아닌 것은 무엇인가요?',
         'choices': ['영상 촬영', '사물 인식 기술', '자율주행 자동차', '음성인식과 음성합성'],
         'answer': 1,
         'explain': '영상 촬영도 AI의 도움을 받을 수는 있으나 단순한 영상 촬영은 인공지능과 관련이 없습니다.'},
        {'no': 2, 'kind': 'fill', 'points': 10, 'label': '실습 A형',
         'text': '다음은 진수가 교실에 들어오다 코디니와 인사를 한 후, 코디니에게 다가가는 장면을 구현한 코드입니다. 붉은색 네모박스로 표시한 부분의 잘못된 명령 블록을 올바르게 바꾸어 보세요.',
         'image': IMG + 'q2.jpg', 'choices': CIRCLED, 'answer': 2,
         'explain': '오브젝트에 설정된 이동 방향은 오른쪽 방향이며, 문제에서는 왼쪽 방향으로 진행하므로 -50만큼 이동해야 합니다. (정답 ② 이동방향으로 -50 만큼 이동)'},
        {'no': 3, 'kind': 'fill', 'points': 10, 'label': '실습 A형',
         'text': '다음은 코디니가 불고기 버거를 사러 햄버거 가게에 간 장면입니다. 처음 시작할 때 불고기 버거가 보이지 않게 하려면 빈칸에 어떤 블록이 들어가야 할까요?',
         'image': IMG + 'q3.jpg', 'choices': CIRCLED, 'answer': 3,
         'explain': "불고기 버거를 보이지 않게 하려면 '불고기 버거 감추기' 블록을 사용하여야 합니다. (정답 ③ 오브젝트 불고기버거 감추기)"},
        {'no': 4, 'kind': 'fill', 'points': 10, 'label': '실습 A형',
         'text': "다음은 변수 '엄마'에 엄마 전화번호를 입력한 후, 지니를 호출하고, 엄마 전화번호를 물어보면 안내해 주는 프로그램입니다. 빈칸에 어떤 블록이 들어가야 할까요? (엄마 전화번호는 010-1234-5678입니다.)",
         'image': IMG + 'q4.jpg', 'choices': CIRCLED, 'answer': 1,
         'explain': "이 문제에서 변수는 '엄마'입니다. 따라서 변수 '엄마'에 전화번호를 저장합니다. 변수 이름이 '전화번호'가 아니라는 점에 유의하세요."},
        {'no': 5, 'kind': 'fill', 'points': 10, 'label': '실습 A형',
         'text': '코디니가 극장에 왔습니다. 코디니가 좌석까지 이동하기 위해서는 빈칸에 어떤 블록이 들어가야 할까요?',
         'image': IMG + 'q5.jpg', 'choices': CIRCLED, 'answer': 1,
         'explain': '이 문제에서 움직이는 오브젝트는 코디니입니다. (정답 ① 오브젝트 선택 코디니)'},
        {'no': 6, 'kind': 'build', 'points': 15, 'label': '실습 B형',
         'text': '코디니가 목적지까지 갈 수 있도록 코딩해 보세요.',
         'image': IMG + 'q6.jpg', 'answer_image': IMG + 'a6.jpg',
         'explain': '코디니가 위로 갈 때에는 y 값이 양수, 아래로 갈 때에는 y 값이 음수이며, 오른쪽으로 갈 때에는 x 값이 양수이고 왼쪽으로 갈 때에는 x 값이 음수입니다.'},
        {'no': 7, 'kind': 'build', 'points': 15, 'label': '실습 B형',
         'text': '알라딘이 지니를 부르면 지니는 몇 번 불렸는지 대답합니다. 변수를 사용하여 호출어 지니를 부를 때마다 지니를 부른 횟수를 말해 주는 프로그램을 코딩하세요.',
         'image': IMG + 'q7.jpg', 'answer_image': IMG + 'a7.jpg',
         'explain': "지니를 부를 때마다 변수 '횟수'에 1씩 더해서 새로 저장됩니다."},
        {'no': 8, 'kind': 'build', 'points': 20, 'label': '프로젝트형',
         'text': '방송국에서 동물원 취재를 왔어요. 사자와 하마의 영상을 찍을 수 있도록 카메라 맨을 움직이는 코딩을 해 보세요.',
         'image': IMG + 'q8.jpg', 'answer_image': IMG + 'a8.jpg',
         'explain': '① 카메라 맨이 음성합성으로 동물원에 온 목적과 영상을 찍겠다고 말합니다. ② 찍을 동물 이름을 말해 줍니다. ③ 카메라 맨이 찍을 동물이 있는 근처로 이동합니다(좌표 활용). ④ 카메라 맨이 찍는 동물의 소리가 3초간 재생됩니다. 이후 다른 동물을 말하면 같은 방법으로 구현됩니다.'},
    ],
}

it = Item.objects.get(id=1178)
it.exam_data = json.dumps(data, ensure_ascii=False)
it.requires_coding = True
it.save(update_fields=['exam_data', 'requires_coding'])
print('saved', it.id, it.title, len(it.exam_data))
