"""올로AI 1단계: 어린이 눈높이 설명 · 개념 게임 · 낱말 그림 · 교과 연계 한마디.

EASY[수업키] = {
  'easy': [(큰 그림 글자, 한 줄 제목, 아주 쉬운 설명)],   # 다섯 살도 알아들을 말로
  'play': {'id': 게임 이름(_robot_games.html), 'title', 'how'},
  'school': 학교 수업과 어떻게 이어지는지,
  'pics': 낱말 순서대로의 그림. 'crop:교재PDF쪽:x0,y0,x1,y1'(쪽 너비를 800 으로 본 좌표) · 'svg:이름' · 'thumb'
}
"""

EASY = {
    'lv1_01': {
        'easy': [
            ('🖐️', '고무줄을 쭉 당겨 볼까?', '쭈~욱 당겼다가 손을 놓으면 탁! 하고 다시 작아져요.'),
            ('🔙', '원래대로 돌아가고 싶어!', '늘어난 고무줄은 “원래 모양으로 돌아갈래!” 하고 힘을 써요. 이 힘이 탄성력이에요.'),
            ('🏹', '많이 당기면 멀리!', '조금 당기면 화살이 가까이, 많이 당기면 멀리 날아가요.'),
        ],
        'play': {'id': 'bow', 'title': '고무줄 명궁', 'how': '당긴 만큼 세지는 탄성력으로 움직이는 과녁과 바람까지 정복해요. 3단계'},
        'school': '학교에서는 “여러 가지 힘”을 배울 때 탄성력을 만나요.',
        'pics': ['crop:8:112,551,206,601', 'crop:8:112,726,206,776', 'crop:8:112,788,206,836', 'crop:8:112,906,206,956', 'crop:8:112,848,206,896', 'crop:8:112,964,206,1014'],
    },
    'lv1_02': {
        'easy': [
            ('🦒', '긴 팔은 멀리 닿아요', '팔이 길면 멀리 있는 것도 톡! 크게 움직여요. 그런데 무거운 걸 밀기는 힘들어요.'),
            ('💪', '짧은 팔은 힘이 세요', '팔이 짧으면 조금만 움직이지만 “끙!” 하고 센 힘을 낼 수 있어요.'),
        ],
        'play': {'id': 'arm', 'title': '로봇 팔 설계소', 'how': '팔 길이를 정해 닿는 거리와 힘을 모두 만족시키는 임무를 해결해요. 3단계'},
        'school': '학교 체육 시간의 앞구르기처럼, 몸을 어떻게 쓰느냐에 따라 움직임이 달라져요.',
        'pics': ['crop:16:603,528,723,646', 'crop:8:112,964,206,1014', 'crop:16:92,342,446,458'],
    },
    'lv1_03': {
        'easy': [
            ('⚽', '동글동글하면 잘 굴러요', '공은 데굴데굴! 네모난 상자는 덜컹! 바퀴가 동그라면 부드럽게 굴러가요.'),
            ('📏', '가운데에서 끝까지 똑같아', '동그라미는 한가운데에서 끝까지 거리가 어디나 같아요. 그래서 위아래로 흔들리지 않아요.'),
        ],
        'play': {'id': 'wheel', 'title': '달걀 배달 대작전', 'how': '바퀴 모양을 고르고 속도를 조절해 달걀을 깨뜨리지 않고 배달해요. 3단계'},
        'school': '학교 수학 시간에 “원”의 중심과 반지름을 배워요.',
        'pics': ['svg:circle', 'svg:center', 'crop:24:152,746,398,870'],
    },
    'lv1_04': {
        'easy': [
            ('🧹', '넓으면 한 번에 많이!', '작은 숟가락보다 큰 삽이 한 번에 더 많이 옮겨요. 불도저의 앞판도 아주 넓어요.'),
            ('👉', '밀면 움직여요', '무거운 것을 들지 않아도, 뒤에서 쭈욱 밀면 옮길 수 있어요.'),
        ],
        'play': {'id': 'snow', 'title': '눈 치우기 대장', 'how': '불도저를 직접 운전하며 상황에 맞는 판 넓이를 골라 눈을 치워요. 3단계'},
        'school': '학교 겨울 수업의 눈 치우기 놀이와 이어져요.',
        'pics': ['thumb', 'svg:snowplow', 'crop:72:133,558,228,648'],
    },
    'lv1_05': {
        'easy': [
            ('🎡', '빙글빙글 = 회전 운동', '선풍기 날개처럼 한 자리에서 계속 도는 거예요.'),
            ('🛝', '왔다 갔다 = 왕복 운동', '그네처럼 갔다가 다시 돌아오는 거예요.'),
            ('🐦', '막대를 이으면 바뀌어요', '빙글 도는 모터에 막대를 이으면 날개가 위아래로 펄럭펄럭!'),
        ],
        'play': {'id': 'spin', 'title': '움직임 감별사', 'how': '기계가 남기는 빨간 자국을 보고 회전 운동과 왕복 운동을 가려내요. 3단계'},
        'school': '학교 체육·과학에서 배우는 “회전 운동”이에요.',
        'pics': ['crop:40:554,386,720,586', 'crop:40:482,798,718,1012', 'crop:48:106,386,292,533'],
    },
    'lv1_06': {
        'easy': [
            ('🔄', '모터는 빙글 돌기만 해요', '모터 혼자서는 주먹을 뻗지 못해요. 그냥 빙글빙글 돌 뿐이에요.'),
            ('🥊', '막대가 도와줘요', '막대를 이어 주면 도는 힘이 “앞으로 쭉! 뒤로 쏙!” 주먹 동작으로 바뀌어요.'),
        ],
        'play': {'id': 'punch', 'title': '크랭크 복싱', 'how': '연결 구멍을 골라 주먹 거리를 맞추고 타이밍 펀치를 날려요. 3단계'},
        'school': '학교 과학 시간에 전기로 돌아가는 “모터”를 배워요.',
        'pics': ['crop:48:106,542,292,673', 'svg:cw', 'svg:ccw'],
    },
    'lv1_07': {
        'easy': [
            ('✂️', '가위를 벌려 봐!', '가위를 조금 벌리면 작은 각, 활짝 벌리면 큰 각! 벌어진 정도가 각도예요.'),
            ('📐', '네모 모서리는 직각', '책의 모서리처럼 반듯한 각이 직각(90도)이에요. 더 좁으면 예각, 더 넓으면 둔각!'),
            ('🐛', '애벌레는 접었다 폈다', '몸을 접으면 짧아지고 펴면 길어져요. 그렇게 꿈틀꿈틀 앞으로 가요.'),
        ],
        'play': {'id': 'angle', 'title': '각도 레이저 사냥', 'how': '레이저의 각도를 돌려 말하는 각도의 풍선을 터뜨려요. 3단계'},
        'school': '학교 수학 시간에 각도기를 쓰며 배워요.',
        'pics': ['crop:56:112,335,232,468', 'crop:56:240,335,356,468', 'crop:56:536,335,716,468', 'svg:irsensor'],
    },
    'lv1_08': {
        'easy': [
            ('1️⃣', '하나씩 차례차례', '양말을 신고 신발을 신어요. 순서가 바뀌면 이상하지요? 로봇도 위에서부터 차례로 해요.'),
            ('🔁', '또 해! 또 해!', '“박수 다섯 번”처럼 같은 일을 여러 번 하는 것이 반복이에요.'),
        ],
        'play': {'id': 'blocks', 'title': '황소 코딩 탐험', 'how': '명령 블록을 순서대로 담고 반복까지 써서 별을 모아 도착해요. 3단계'},
        'school': '학교 실과 시간에 로봇이 움직이는 원리를 배워요.',
        'pics': ['svg:sequence', 'svg:repeat', 'crop:8:112,666,206,718'],
    },
    'lv1_09': {
        'easy': [
            ('🍚', '움직이려면 힘이 필요해', '우리가 밥을 먹고 힘을 내듯, 기계도 힘을 내려면 먹을 것이 필요해요.'),
            ('🔋', '로봇의 밥은 전기!', '자동차는 기름을, 로봇은 전기를 먹고 모터를 돌려요. 일하게 하는 이 힘이 동력이에요.'),
        ],
        'play': {'id': 'power', 'title': '에너지 충전소', 'how': '손님마다 알맞은 에너지를 빠르게 골라 주는 충전소 사장님이 되어요. 3단계'},
        'school': '학교 과학 시간에 여러 가지 “에너지”를 배워요.',
        'pics': ['crop:72:106,305,392,437', 'crop:72:548,536,674,656', 'svg:engine', 'svg:linetrace'],
    },
    'lv1_10': {
        'easy': [
            ('🪑', '다리 세 개면 안 넘어져', '의자 다리가 세 군데에서 받쳐 주면 흔들리지 않아요.'),
            ('🐞', '곤충은 번갈아 세 다리씩', '다리 세 개로 땅을 짚고, 나머지 세 개를 옮겨요. 그래서 걸을 때도 안 넘어져요.'),
        ],
        'play': {'id': 'bug', 'title': '곤충 걸음 훈련소', 'how': '다리를 직접 들어 올려 넘어지지 않고 걷는 방법을 찾아요. 3단계'},
        'school': '학교 과학 시간에 곤충의 생김새와 한살이를 배워요.',
        'pics': ['crop:80:108,352,323,466', 'svg:gravity', 'crop:80:104,578,286,712'],
    },
    'lv1_11': {
        'easy': [
            ('🚌', '버스가 끼익!', '달리던 버스가 갑자기 서면 몸이 앞으로 쏠려요. 몸은 계속 가고 싶거든요.'),
            ('🚦', '버스가 부웅!', '서 있던 버스가 갑자기 출발하면 몸이 뒤로 쏠려요. 몸은 그대로 있고 싶거든요.'),
            ('🌀', '팽이는 계속 돌고 싶어', '하던 대로 계속하려는 것이 관성이에요. 그래서 팽이는 한참 동안 돌아요.'),
        ],
        'play': {'id': 'inertia', 'title': '안전 운전 버스', 'how': '가속과 브레이크를 조절해 승객이 넘어지지 않게 정류장에 멈춰요. 3단계'},
        'school': '중학교·고등학교 과학에서 “관성의 법칙”으로 더 자세히 배워요.',
        'pics': ['crop:88:128,325,392,446', 'crop:88:158,486,332,592', 'crop:88:106,772,298,922'],
    },
    'lv1_12': {
        'easy': [
            ('🦴', '돌 속에 남은 흔적', '아주아주 옛날 공룡의 뼈와 발자국이 돌이 되어 남았어요. 그게 화석이에요.'),
            ('🍖', '고기 냠냠, 풀 냠냠', '뾰족한 이빨은 고기를 먹는 공룡, 넓적한 이빨은 풀을 먹는 공룡이에요.'),
        ],
        'play': {'id': 'dino', 'title': '화석 발굴단', 'how': '땅을 파서 화석을 찾고, 단서로 어떤 공룡인지와 먹이를 알아내요. 3단계'},
        'school': '학교 과학 시간에 “지층과 화석”을 배워요.',
        'pics': ['svg:fossil', 'crop:96:126,514,278,652', 'crop:96:326,514,474,652'],
    },
}


def _svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 120" width="400" height="240" '
            'font-family="sans-serif" font-weight="700"><rect width="200" height="120" fill="#fff"/>' + body + '</svg>')


_ARROW = '<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="#e11d48"/></marker></defs>'

ART = {
    'circle': _svg('<circle cx="100" cy="60" r="48" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="5"/>'),
    'center': _svg('<circle cx="100" cy="60" r="48" fill="#eff6ff" stroke="#1d4ed8" stroke-width="4"/>'
                   '<path d="M100 60H148M100 60V12M100 60L66 94" stroke="#e11d48" stroke-width="3" stroke-dasharray="6 4"/>'
                   '<circle cx="100" cy="60" r="7" fill="#e11d48"/><text x="68" y="55" font-size="15" fill="#111">중심</text>'),
    'snowplow': _svg('<rect y="96" width="200" height="24" fill="#e0f2fe"/><rect x="62" y="48" width="86" height="34" rx="5" fill="#f59e0b"/>'
                     '<rect x="96" y="24" width="40" height="28" rx="4" fill="#fbbf24"/><rect x="104" y="30" width="24" height="16" fill="#bae6fd"/>'
                     '<path d="M52 40Q30 66 46 96L62 96V48z" fill="#64748b"/><circle cx="82" cy="88" r="14" fill="#1f2937"/><circle cx="130" cy="88" r="14" fill="#1f2937"/>'
                     '<circle cx="22" cy="94" r="14" fill="#fff" stroke="#93c5fd" stroke-width="2"/><circle cx="38" cy="100" r="10" fill="#fff" stroke="#93c5fd" stroke-width="2"/>'),
    'cw': _svg(_ARROW + '<circle cx="100" cy="60" r="34" fill="#fef3c7" stroke="#92400e" stroke-width="3"/><path d="M100 60V34M100 60L118 70" stroke="#111" stroke-width="4"/>'
               '<path d="M100 14A46 46 0 1 1 55 70" fill="none" stroke="#e11d48" stroke-width="6" marker-end="url(#a)"/>'),
    'ccw': _svg(_ARROW + '<circle cx="100" cy="60" r="34" fill="#fef3c7" stroke="#92400e" stroke-width="3"/><path d="M100 60V34M100 60L82 70" stroke="#111" stroke-width="4"/>'
                '<path d="M100 14A46 46 0 1 0 145 70" fill="none" stroke="#e11d48" stroke-width="6" marker-end="url(#a)"/>'),
    'irsensor': _svg('<rect x="14" y="36" width="52" height="48" rx="8" fill="#475569"/><circle cx="66" cy="50" r="7" fill="#e11d48"/><circle cx="66" cy="72" r="7" fill="#111"/>'
                     '<path d="M78 50H150M150 72H82" stroke="#e11d48" stroke-width="3" stroke-dasharray="8 5"/><path d="M142 44L154 50L142 56M90 66L78 72L90 78" fill="none" stroke="#e11d48" stroke-width="3"/>'
                     '<rect x="158" y="22" width="26" height="76" rx="4" fill="#a16207"/><text x="86" y="30" font-size="13" fill="#111">앞에 뭐가 있나?</text>'),
    'sequence': _svg(_ARROW + '<g font-size="14" fill="#fff"><rect x="50" y="8" width="100" height="28" rx="7" fill="#2563eb"/><text x="78" y="27">① 앞으로</text>'
                     '<rect x="50" y="46" width="100" height="28" rx="7" fill="#7c3aed"/><text x="72" y="65">② 기다리기</text>'
                     '<rect x="50" y="84" width="100" height="28" rx="7" fill="#059669"/><text x="86" y="103">③ 멈춤</text></g>'
                     '<path d="M26 14V104" stroke="#e11d48" stroke-width="5" marker-end="url(#a)"/>'),
    'repeat': _svg(_ARROW + '<path d="M66 28A44 40 0 1 1 56 80" fill="none" stroke="#e11d48" stroke-width="9" marker-end="url(#a)"/>'
                   '<text x="76" y="68" font-size="22" fill="#111">또! 또!</text>'),
    'engine': _svg('<rect x="52" y="44" width="96" height="58" rx="8" fill="#64748b"/><g fill="#94a3b8"><rect x="62" y="22" width="20" height="24"/><rect x="90" y="22" width="20" height="24"/><rect x="118" y="22" width="20" height="24"/></g>'
                   '<circle cx="42" cy="73" r="18" fill="#1f2937"/><circle cx="42" cy="73" r="6" fill="#cbd5e1"/><text x="74" y="80" font-size="18" fill="#fff">엔진</text>'
                   '<path d="M174 40q16 22 0 32q-16-10 0-32" fill="#f59e0b"/><text x="160" y="96" font-size="13" fill="#111">연료</text>'),
    'linetrace': _svg('<path d="M10 100C60 100 60 40 110 40S160 80 192 60" fill="none" stroke="#111" stroke-width="12" stroke-linecap="round"/>'
                      '<g transform="translate(70 34) rotate(-28)"><rect x="-4" y="0" width="52" height="30" rx="7" fill="#22c55e"/><circle cx="8" cy="32" r="7" fill="#111"/><circle cx="36" cy="32" r="7" fill="#111"/><circle cx="42" cy="12" r="4" fill="#e11d48"/></g>'),
    'gravity': _svg('<path d="M60 96H140L100 22z" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="3"/><circle cx="100" cy="70" r="8" fill="#e11d48"/>'
                    '<path d="M100 70V106" stroke="#e11d48" stroke-width="3" stroke-dasharray="6 4"/><rect x="30" y="97" width="140" height="8" fill="#78716c"/><text x="114" y="66" font-size="13" fill="#111">무게 중심</text>'),
    'fossil': _svg('<ellipse cx="100" cy="62" rx="90" ry="52" fill="#d6b88a"/><g stroke="#6b4f2a" stroke-width="5" fill="none" stroke-linecap="round">'
                   '<path d="M52 66C80 52 120 52 150 70"/><path d="M70 58q-4 20 6 34M88 54q-2 24 8 40M108 55q0 22 12 34M126 60q4 16 16 22"/></g>'
                   '<ellipse cx="42" cy="58" rx="19" ry="13" fill="#f5e6c8" stroke="#6b4f2a" stroke-width="3"/><circle cx="37" cy="55" r="4" fill="#6b4f2a"/>'),
}
