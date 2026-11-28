"""코딩기초(블록코딩) 미션 과정 내용. 메듀코드의 미션 모드(/meducode/?mission=1)로 푼다.

각 미션은 Item.mission_data 에 저장된다 (management command: seed_coding_missions).

지도 글자: S 출발, G 깃발, * 보석, . 길, # 나무(못 감)
그림 미션의 좌표: 무대 가운데가 (0, 0), 오른쪽 +x, 위쪽 +y. 방향 0=위, 90=오른쪽
solution 은 모범 풀이(블록 순서). 별 3개 기준 블록 수(par)를 여기서 세고, 점검할 때 그대로 실행해 본다.
"""

PROGRAM_NAME = '코딩기초'

DESCRIPTION = (
    '메듀코드 블록으로 로봇을 움직여 미션을 해결하며 배우는 블록코딩 기초 과정입니다. '
    '순서 → 방향 → 반복 → 그림 그리기 → 만약(조건) → 도전(변수·키보드 조종) 순서로, '
    '미션을 성공하면 별을 받고 다음 미션으로 나아갑니다.'
)

# ---- 블록 묶음 ----
MOVE = {'name': '🚶 움직임', 'colour': '#1E88E5', 'types': ['mi_forward', 'mi_turn']}
STRAIGHT = {'name': '🚶 움직임', 'colour': '#1E88E5', 'types': ['mi_forward']}
GEM = {'name': '💎 보석', 'colour': '#8E44AD', 'types': ['mi_collect']}
SAY = {'name': '💬 말하기', 'colour': '#00BCD4', 'types': ['medu_say']}
REPEAT = {'name': '🔁 반복', 'colour': '#43A047', 'types': ['controls_repeat_ext']}
UNTIL = {'name': '🔁 반복', 'colour': '#43A047', 'types': ['mi_until_goal', 'controls_repeat_ext']}
IF = {'name': '🔀 만약', 'colour': '#607D8B', 'types': ['controls_if', 'controls_if_else']}
SENSE = {'name': '👀 살피기', 'colour': '#7CB342', 'types': ['mi_path', 'mi_gem_here', 'mi_at_goal']}
PEN = {'name': '✏️ 붓', 'colour': '#8D6E63', 'types': ['medu_pen_down', 'medu_pen_up']}
DRAW = {'name': '🚶 움직임', 'colour': '#1E88E5', 'types': ['medu_move_dir', 'medu_rotate']}
BOX = {'name': '📦 변수', 'colour': '#E53935', 'types': ['medu_var_set', 'medu_var_change', 'medu_var_get']}
KEYS = {'name': '⌨️ 키보드', 'colour': '#FF9800',
        'types': ['medu_when_key:ArrowUp', 'medu_when_key:ArrowLeft', 'medu_when_key:ArrowRight', 'medu_when_key:Space']}

NEED_REPEAT = {'require': ['controls_repeat_ext'], 'requireText': '"회 반복" 블록을 사용해서 해결해 보세요'}


def mission(title, story, learn, goals, hints, spec, solution):
    return {'title': title, 'story': story, 'learn': learn, 'goals': goals, 'hints': hints,
            'spec': spec, 'solution': solution}


def maze(rows, blocks, dir='E', **extra):
    return {'type': 'maze', 'map': rows, 'dir': dir, 'blocks': blocks, **extra}


def draw(target, start, blocks, **extra):
    return {'type': 'draw', 'target': target, 'start': {'x': start[0], 'y': start[1], 'dir': start[2]},
            'blocks': blocks, **extra}


def path(*points):
    """점들을 차례로 잇는 선 목록."""
    return [[*a, *b] for a, b in zip(points, points[1:])]


def repeat(times, *body):
    return ('repeat', times, list(body))


F, L, R, C = 'F', 'L', 'R', 'C'
PEN_DOWN = 'pen'


def move(steps):
    return ('move', steps)


def turn(angle):
    return ('turn', angle)


# 단원마다 배우는 생각: (이름, 아주 쉬운 설명, 생활 속 예)
CHAPTERS = [
    {
        'title': '블록코딩 처음 만나기',
        'goal': '블록을 위에서 아래로 차례차례 연결하면 컴퓨터가 그 순서대로 움직인다는 것을 알아요.',
        'idea': {'icon': '🪜', 'name': '순서', 'easy': '컴퓨터는 위에 있는 블록부터 하나씩, 차례차례 따라 해요.',
                 'example': '양말을 신고 → 신발을 신어요. 순서가 바뀌면 이상해지죠?'},
        'missions': [
            mission(
                '첫걸음! 깃발까지 가기', '로봇 메듀가 처음으로 눈을 떴어요. 앞에 보이는 빨간 깃발까지 데려다 주세요.',
                '블록 하나는 명령 하나예요. "시작하기" 블록 안에 차례로 끼워 넣어요.',
                ['깃발 🏁 에 도착하기'],
                ['왼쪽 "움직임"을 눌러 블록을 꺼내요.', '깃발까지 몇 칸인지 손가락으로 세어 보세요.'],
                maze(['S..G'], [STRAIGHT]), [F, F, F]),
            mission(
                '도착해서 인사하기', '깃발 앞에 친구가 기다리고 있어요. 도착한 다음 "안녕!" 하고 인사해요.',
                '움직이는 블록과 말하는 블록도 순서대로 놓으면 차례로 실행돼요.',
                ['깃발 🏁 에 도착하기', '"안녕!" 이라고 말하기'],
                ['먼저 다 움직인 다음에 말해야 친구가 들어요.', '"말하기" 블록 칸의 글자는 "안녕!" 그대로 두면 돼요.'],
                maze(['S...G'], [STRAIGHT, SAY], say='안녕', sayFail='"안녕!" 이라고 인사해 주세요'),
                [F, F, F, F, ('say', '안녕!')]),
            mission(
                '반짝 보석 줍기', '길 위에 보석이 떨어져 있어요. 보석을 모두 주우면서 깃발까지 가요.',
                '보석이 있는 칸에 도착했을 때 "보석 줍기"를 해야 주워져요. 순서가 중요해요!',
                ['보석 💎 2개 모두 줍기', '깃발 🏁 에 도착하기'],
                ['보석 칸까지 간 다음 바로 "보석 줍기"를 놓아요.', '앞으로 → 앞으로 → 줍기 … 이런 순서예요.'],
                maze(['S.*.*G'], [STRAIGHT, GEM]), [F, F, C, F, F, C, F]),
        ],
    },
    {
        'title': '방향 바꾸기',
        'goal': '왼쪽과 오른쪽을 로봇의 눈으로 생각하며 꺾인 길을 지나가요.',
        'idea': {'icon': '🧭', 'name': '방향', 'easy': '"돌기"는 제자리에서 몸만 돌려요. 앞으로 가려면 "앞으로"가 또 필요해요.',
                 'example': '내가 로봇이라고 생각하고, 로봇의 코가 향한 쪽에서 왼쪽·오른쪽을 정해요.'},
        'missions': [
            mission(
                'ㄱ자 길 돌기', '길이 중간에 꺾여 있어요. 방향을 돌려서 깃발까지 가 보세요.',
                '로봇 머리의 주황색 화살표가 앞이에요. 꺾이는 칸에서 돌아요.',
                ['깃발 🏁 에 도착하기'],
                ['꺾이는 칸까지 먼저 가요.', '로봇이 오른쪽을 보고 있을 때, 아래로 가려면 "오른쪽으로 돌기"예요.'],
                maze(['S..', '##.', '##G'], [MOVE]), [F, F, R, F, F]),
            mission(
                '지그재그 숲길', '구불구불한 숲길이에요. 왼쪽, 오른쪽을 잘 골라야 해요.',
                '돌 때마다 로봇이 바라보는 쪽이 바뀌어요. 한 번 돌 때마다 확인해요.',
                ['깃발 🏁 에 도착하기'],
                ['한 칸 가고 돌기가 계속 번갈아 나와요.', '아래를 보던 로봇이 오른쪽(화면)으로 가려면 로봇의 "왼쪽"이에요.'],
                maze(['S.###', '#..##', '##.G#'], [MOVE]), [F, R, F, L, F, R, F, L, F]),
            mission(
                '갈림길 보석 찾기', '위쪽 끝과 오른쪽 끝에 보석이 하나씩 있어요. 모두 찾아서 아래 깃발로 가요.',
                '긴 문제는 "첫 번째 보석 → 두 번째 보석 → 깃발"처럼 작게 나누면 쉬워져요.',
                ['보석 💎 2개 모두 줍기', '깃발 🏁 에 도착하기'],
                ['뒤로 돌려면 같은 쪽으로 두 번 돌아요.', '먼저 위쪽 보석을 줍고 갈림길로 돌아와요.'],
                maze(['#*###', '#.###', 'S...*', '###.#', '###G#'], [MOVE, GEM]),
                [F, L, F, F, C, R, R, F, F, L, F, F, F, C, R, R, F, L, F, F]),
        ],
    },
    {
        'title': '반복 블록 활용하기',
        'goal': '같은 일을 여러 번 할 때는 반복 블록 하나로 짧게 만들어요.',
        'idea': {'icon': '🔁', 'name': '반복', 'easy': '"3회 반복" 안에 넣으면 그 안의 블록을 3번 해 줘요.',
                 'example': '"박수 쳐! 박수 쳐! 박수 쳐!" 대신 "박수 3번 쳐!" 라고 말해요.'},
        'missions': [
            mission(
                '긴 길을 한 번에', '아주 긴 길이에요. 블록을 7개나 놓지 말고 반복으로 줄여 봐요.',
                '반복 블록의 숫자를 바꾸면 반복하는 횟수가 달라져요.',
                ['"회 반복" 블록 사용하기', '깃발 🏁 에 도착하기'],
                ['반복 블록 안에 "앞으로 한 칸 가기"를 넣어요.', '깃발까지 몇 칸인지 세어서 숫자를 바꿔요.'],
                maze(['S......G'], [STRAIGHT, REPEAT], **NEED_REPEAT), [repeat(7, F)]),
            mission(
                '계단 내려가기', '똑같이 생긴 계단이 계속 이어져요. 계단 한 칸을 만드는 방법을 찾아 반복해요.',
                '되풀이되는 모양(패턴)을 찾으면, 그 한 묶음만 만들고 반복하면 돼요.',
                ['"회 반복" 블록 사용하기', '깃발 🏁 에 도착하기'],
                ['계단 한 칸: 앞으로 → 오른쪽 → 앞으로 → 왼쪽', '계단이 몇 개인지 세어 보세요.'],
                maze(['S.###', '#..##', '##..#', '###..', '####G'], [MOVE, REPEAT], **NEED_REPEAT),
                [repeat(4, F, R, F, L)]),
            mission(
                '네모 길의 보석', '네모난 길의 모서리마다 보석이 있어요. 반복 안에 반복을 넣으면 아주 짧아져요.',
                '반복 블록 안에 또 반복 블록을 넣을 수 있어요. 이것을 "겹친 반복"이라고 해요.',
                ['보석 💎 3개 모두 줍기', '"회 반복" 블록 사용하기'],
                ['한 변: 앞으로 3번 → 보석 줍기 → 오른쪽 돌기', '이 한 변을 3번 반복해요.'],
                maze(['S..*', '.##.', '.##.', '*..*'], [MOVE, GEM, REPEAT], **NEED_REPEAT),
                [repeat(3, repeat(3, F), C, R)]),
        ],
    },
    {
        'title': '그림 그리기',
        'goal': '붓을 내리고 움직이면 선이 그려져요. 각도와 반복으로 도형을 만들어요.',
        'idea': {'icon': '📐', 'name': '각도', 'easy': '90만큼 돌면 직각(ㄱ자), 360만큼 돌면 한 바퀴예요.',
                 'example': '한 바퀴 360을 4번에 나눠 돌면 90씩 → 네모가 돼요. 3번에 나누면 120씩 → 세모!'},
        'missions': [
            mission(
                'ㄱ 그리기', '회색 선을 따라 붓으로 "ㄱ" 글자를 써 보세요.',
                '"그리기 시작하기"를 먼저 해야 지나간 자리에 선이 남아요.',
                ['회색 선을 모두 따라 그리기'],
                ['그리기 시작하기 → 120만큼 움직이기 → 방향 돌리기 → 80만큼 움직이기', '숫자를 눌러 바꿀 수 있어요.'],
                draw(path((-60, 40), (60, 40), (60, -40)), (-60, 40, 90), [PEN, DRAW]),
                [PEN_DOWN, move(120), turn(90), move(80)]),
            mission(
                '네모 그리기', '네 변의 길이가 모두 100인 네모를 그려요.',
                '네모는 "앞으로 가고 90 돌기"를 4번 되풀이한 모양이에요.',
                ['회색 네모를 모두 따라 그리기', '"회 반복" 블록 사용하기'],
                ['"그리기 시작하기"는 반복 밖에 한 번만!', '반복 안: 100만큼 움직이기 → 90만큼 회전하기'],
                draw(path((-50, 50), (50, 50), (50, -50), (-50, -50), (-50, 50)), (-50, 50, 90), [PEN, DRAW, REPEAT], **NEED_REPEAT),
                [PEN_DOWN, repeat(4, move(100), turn(90))]),
            mission(
                '세모 그리기', '길이가 140인 세모를 그려요. 몇 번, 얼마나 돌아야 할까요?',
                '한 바퀴(360)를 모서리 수로 나눈 만큼 돌아요.',
                ['회색 세모를 모두 따라 그리기', '"회 반복" 블록 사용하기'],
                ['360 나누기 3 은?', '반복 안: 140만큼 움직이기 → 120만큼 회전하기'],
                draw(path((-70, -60), (0, 61), (70, -60), (-70, -60)), (-70, -60, 30), [PEN, DRAW, REPEAT], **NEED_REPEAT),
                [PEN_DOWN, repeat(3, move(140), turn(120))]),
        ],
    },
    {
        'title': '만약에 (조건)',
        'goal': '상황을 살펴보고 "만약 ~라면" 으로 로봇이 스스로 판단하게 해요.',
        'idea': {'icon': '🚦', 'name': '조건', 'easy': '"만약 ~라면" 안의 블록은 그 말이 맞을 때만 해요.',
                 'example': '만약 비가 오면 우산을 써요. 아니면 그냥 나가요.'},
        'missions': [
            mission(
                '보석이 있으면 줍기', '긴 길 곳곳에 보석이 있어요. 칸마다 살펴보고, 있을 때만 주워요.',
                '반복하면서 매번 "여기에 보석이 있는가?" 를 확인하면, 어디에 있어도 주울 수 있어요.',
                ['보석 💎 3개 모두 줍기', '"만약" 블록 사용하기', '깃발 🏁 에 도착하기'],
                ['반복 안: 앞으로 → 만약 보석이 있으면 → 줍기', '보석이 없는 칸에서 "줍기"를 하면 실패해요.'],
                maze(['S.*..*.*.G'], [STRAIGHT, GEM, REPEAT, IF, SENSE],
                     require=['controls_if'], requireText='"만약" 블록으로 보석이 있는지 살펴보며 주워 보세요'),
                [repeat(9, F, ('if', 'gem', [C]))]),
            mission(
                '빙글빙글 달팽이 길', '막힌 곳에서는 늘 오른쪽으로 꺾이는 길이에요. 로봇이 스스로 길을 찾게 해요.',
                '"깃발에 도착할 때까지 반복"은 몇 번 해야 할지 몰라도 끝까지 해 줘요.',
                ['"만약 ~ 아니면" 블록 사용하기', '깃발 🏁 에 도착하기'],
                ['만약 앞에 길이 있으면 → 앞으로', '아니면 → 오른쪽으로 돌기'],
                maze(['S......', '######.', '..G###.', '.#####.', '.......'], [MOVE, UNTIL, IF, SENSE],
                     require=['controls_if'], requireText='"만약" 블록으로 앞에 길이 있는지 살펴보세요'),
                [('until', [('ifelse', 'ahead', [F], [R])])]),
            mission(
                '똑똑한 길 찾기', '왼쪽, 오른쪽이 섞인 길이에요. 어느 쪽에 길이 있는지 살펴서 돌아요.',
                '"만약 ~ 아니면" 안에 또 "만약"을 넣으면 세 가지 경우를 나눌 수 있어요.',
                ['"만약" 블록 사용하기', '깃발 🏁 에 도착하기'],
                ['앞에 길이 있으면 앞으로 가요.', '아니라면: 오른쪽에 길이 있으면 오른쪽, 아니면 왼쪽으로 돌아요.'],
                maze(['S..####','##.####', '##...##', '####.##', '####..G'], [MOVE, UNTIL, IF, SENSE],
                     require=['controls_if'], requireText='"만약" 블록으로 길을 살펴보세요'),
                [('until', [('ifelse', 'ahead', [F], [('ifelse', 'right', [R], [L])])])]),
        ],
    },
    {
        'title': '도전! 코딩 모험',
        'goal': '지금까지 배운 것을 합치고, 값을 담는 변수와 키보드 조종에 도전해요.',
        'idea': {'icon': '📦', 'name': '변수와 이벤트', 'easy': '변수는 숫자를 담아 두는 상자, 이벤트는 "이럴 때 해!" 라는 신호예요.',
                 'example': '저금통에 동전이 들어올 때마다 1씩 세요. 초인종이 울리면 문을 열어요.'},
        'missions': [
            mission(
                '바람개비 그리기', '네모 4개를 빙 돌려 그리면 바람개비가 돼요.',
                '네모 그리기(반복)를 통째로 다시 반복해요.',
                ['회색 바람개비를 모두 따라 그리기', '"회 반복" 블록 사용하기'],
                ['안쪽 반복: 60만큼 움직이고 90 돌기를 4번 → 네모 하나', '네모 하나를 그린 뒤 90 돌고, 이것을 4번 반복해요.'],
                draw(path((0, 0), (0, 60), (60, 60), (60, 0), (0, 0)) + path((0, 0), (60, 0), (60, -60), (0, -60), (0, 0))
                     + path((0, 0), (0, -60), (-60, -60), (-60, 0), (0, 0)) + path((0, 0), (-60, 0), (-60, 60), (0, 60), (0, 0)),
                     (0, 0, 0), [PEN, DRAW, REPEAT], **NEED_REPEAT),
                [PEN_DOWN, repeat(4, repeat(4, move(60), turn(90)), turn(90))]),
            mission(
                '보석 세기 상자', '보석을 주울 때마다 "보석" 상자에 1씩 담고, 깃발에서 몇 개인지 말해요.',
                '변수는 이름이 붙은 상자예요. 처음에 0으로 설정하고, 주울 때마다 1만큼 더해요.',
                ['보석 💎 모두 줍기', '깃발에서 주운 개수를 말하기'],
                ['처음에 "보석"을 0으로 설정해요.', '"말하기" 칸에 "보석" 블록을 끼워 넣어요.'],
                maze(['S*.**.*.G'], [STRAIGHT, GEM, REPEAT, IF, SENSE, BOX, SAY], variables=['보석'], say='4',
                     sayFail='깃발에 도착한 다음, 주운 보석의 개수를 말해 주세요',
                     require=['medu_var_change'], requireText='보석을 주울 때마다 "보석" 변수에 1만큼 더해 주세요'),
                [('set', 0), repeat(8, F, ('if', 'gem', [C, ('change', 1)])), ('say', ('var',))]),
            mission(
                '내가 조종하는 로봇', '키보드로 로봇을 직접 조종하는 게임을 만들어요. 실행한 다음 방향키를 눌러 보석을 모두 모아요!',
                '"~키를 눌렀을 때" 블록은 그 키를 누를 때마다 안의 블록을 실행해요.',
                ['↑ ← → 키와 스페이스 키에 알맞은 블록 넣기', '조종해서 보석을 모두 줍고 깃발에 도착하기'],
                ['위쪽 화살표 → 앞으로, 왼쪽 화살표 → 왼쪽 돌기, 오른쪽 화살표 → 오른쪽 돌기', '스페이스 → 보석 줍기. 실행한 뒤에 키를 눌러요.'],
                {'type': 'keys', 'map': ['S..*#..', '##.##.#', '#*....*', '#.####.', '#...G..'], 'dir': 'E',
                 'blocks': [KEYS, MOVE, GEM],
                 'starter': ('<xml xmlns="https://developers.google.com/blockly/xml">'
                             '<block type="medu_when_key" x="30" y="30"><field name="KEY">ArrowUp</field>'
                             '<statement name="DO"><block type="mi_forward"></block></statement></block></xml>')},
                [('key', 'ArrowUp', [F]), ('key', 'ArrowLeft', [L]), ('key', 'ArrowRight', [R]), ('key', 'Space', [C])]),
        ],
    },
]


# ---- 모범 풀이 → 블록 XML ----
def _number(name, value, kind='math_number', field='NUM'):
    return f'<value name="{name}"><shadow type="{kind}"><field name="{field}">{value}</field></shadow></value>'


def _condition(kind):
    if kind == 'gem':
        return '<block type="mi_gem_here"></block>'
    if kind == 'goal':
        return '<block type="mi_at_goal"></block>'
    return f'<block type="mi_path"><field name="WHERE">{kind}</field></block>'


def _block(step, variable):
    """(블록 종류, 안쪽 XML, 센 블록 수)"""
    simple = {F: ('mi_forward', ''), C: ('mi_collect', ''), PEN_DOWN: ('medu_pen_down', ''),
              L: ('mi_turn', '<field name="DIR">left</field>'), R: ('mi_turn', '<field name="DIR">right</field>')}
    if isinstance(step, str):
        kind, inner = simple[step]
        return kind, inner, 1
    name = step[0]
    if name == 'repeat':
        body, count = _chain(step[2], variable)
        return 'controls_repeat_ext', f'{_number("TIMES", step[1])}<statement name="DO">{body}</statement>', count + 1
    if name == 'until':
        body, count = _chain(step[1], variable)
        return 'mi_until_goal', f'<statement name="DO">{body}</statement>', count + 1
    if name == 'if':
        body, count = _chain(step[2], variable)
        return 'controls_if', f'<value name="IF0">{_condition(step[1])}</value><statement name="DO0">{body}</statement>', count + 2
    if name == 'ifelse':
        yes, a = _chain(step[2], variable)
        no, b = _chain(step[3], variable)
        inner = (f'<mutation else="1"></mutation><value name="IF0">{_condition(step[1])}</value>'
                 f'<statement name="DO0">{yes}</statement><statement name="ELSE">{no}</statement>')
        return 'controls_if', inner, a + b + 2
    if name == 'move':
        return 'medu_move_dir', f'<field name="DIR">move</field>{_number("STEPS", step[1])}', 1
    if name == 'turn':
        inner = ('<field name="TARGET">rotation</field><field name="MODE">turn</field>'
                 + _number('ANGLE', step[1], 'medu_angle', 'ANGLE'))
        return 'medu_rotate', inner, 1
    if name in ('set', 'change'):
        return f'medu_var_{name}', f'<field name="VAR">{variable}</field>{_number("VALUE", step[1])}', 1
    if name == 'say':
        if isinstance(step[1], str):
            return 'medu_say', f'<value name="VALUE"><shadow type="text"><field name="TEXT">{step[1]}</field></shadow></value>', 1
        return 'medu_say', f'<value name="VALUE"><block type="medu_var_get"><field name="VAR">{variable}</field></block></value>', 2
    raise ValueError(name)


def _chain(steps, variable):
    xml, count = '', 0
    for step in reversed(steps):
        kind, inner, n = _block(step, variable)
        following = f'<next>{xml}</next>' if xml else ''
        xml = f'<block type="{kind}">{inner}{following}</block>'
        count += n
    return xml, count


def solution_xml(data):
    """모범 풀이를 블록 XML 과 블록 수로 바꾼다."""
    variable = (data['spec'].get('variables') or [''])[0]
    steps = data['solution']
    hats, total = [], 0
    if data['spec']['type'] == 'keys':
        for i, (_, key, body) in enumerate(steps):
            inner, count = _chain(body, variable)
            hats.append(f'<block type="medu_when_key" x="30" y="{30 + i * 130}"><field name="KEY">{key}</field>'
                        f'<statement name="DO">{inner}</statement></block>')
            total += count
    else:
        inner, total = _chain(steps, variable)
        hats.append(f'<block type="medu_when_flag_clicked" x="30" y="30"><statement name="DO">{inner}</statement></block>')
    return f'<xml xmlns="https://developers.google.com/blockly/xml">{"".join(hats)}</xml>', total


def item_key(chapter_number, mission_number):
    return f'codingbasics_{chapter_number:02d}_{mission_number:02d}'


def mission_data(chapter_number, mission_number):
    """Item.mission_data 에 저장할 내용."""
    chapter = CHAPTERS[chapter_number - 1]
    data = chapter['missions'][mission_number - 1]
    spec = {'id': item_key(chapter_number, mission_number), 'title': data['title'], **data['spec']}
    if spec['type'] != 'keys':
        spec['par'] = solution_xml(data)[1]
    return {
        'story': data['story'], 'learn': data['learn'], 'goals': data['goals'], 'hints': data['hints'],
        'idea': chapter['idea'], 'spec': spec,
    }


def chapter_content(chapter):
    idea = chapter['idea']
    return f"학습목표: {chapter['goal']}\n주요내용: {idea['icon']} {idea['name']} — {idea['easy']}"
