# 학부모 알림톡 설정 가이드 (솔라피)

## 1. 솔라피 준비
1. solapi.com 가입 → 사업자/본인 인증 → 포인트 충전
2. 발신번호 등록 (알림톡이 실패했을 때 문자로 대신 보낼 번호)
3. 카카오 채널 연동: 솔라피 콘솔 > 카카오 채널 연동 > 기존 비즈니스 채널(메듀랩 AI로봇코딩융합학원) 추가 → `pfId`(KA01PF...) 확인
4. API Key 발급: 설정 > API Key 관리 → API Key / API Secret

## 2. 알림톡 템플릿 2개 등록 (카테고리: 학원/교육, 유형: 기본형)

### 출석 알림
```
[메듀랩] #{학생이름} 학생이 #{날짜} #{시각}에 #{구분}했습니다.
```

### 학원비 청구/미납 안내
```
[메듀랩] #{학생이름} 학생의 #{청구월} #{수업명} 학원비 안내입니다.

- 금액: #{금액}
- 납부기한: #{납부기한}
- 이전 미납: #{이전미납}
- 총 납부할 금액: #{총미납액}
#{납부상태}

아래 버튼으로 바로 결제할 수 있습니다.
```
버튼: 웹링크, 버튼명 `학원비 결제하기`, 모바일/PC 링크 모두 `https://medulab.kr/pay/#{결제코드}/`

변수 이름은 위와 한 글자도 다르면 안 됩니다. 승인 후 각 템플릿 ID(KA01TP...)를 확인합니다.

## 3. 서버 .env (`~/medulab_arcade/medulab_arcade/.env`)
```
SOLAPI_API_KEY=
SOLAPI_API_SECRET=
SOLAPI_PF_ID=KA01PF...
SOLAPI_SENDER=01012345678
SOLAPI_TEMPLATE_ATTENDANCE=KA01TP...
SOLAPI_TEMPLATE_INVOICE=KA01TP...
SOLAPI_SMS_FALLBACK=1   # 0이면 알림톡 실패 시 문자 대체발송 안 함
```
저장 후 `sudo systemctl restart medulab`. 값이 하나라도 비어 있으면 발송하지 않고 기록만 남습니다.

## 4. 미납 안내 예약 (하루 한 번)
```
0 10 * * * cd ~/medulab_arcade/medulab_arcade && venv/bin/python manage.py send_tuition_reminders >> /tmp/tuition_reminders.log 2>&1
```
옵션: `--before 3`(기한 며칠 전부터), `--every 3`(같은 청구서 재안내 최소 간격).

## 5. 확인
- 학부모 회원의 휴대폰 번호가 프로필에 있고, 학생과 '학부모-자녀 연결'이 되어 있어야 합니다.
- 관리자 사이트 > 알림톡 발송 기록에서 발송 완료/실패/건너뜀을 확인합니다.
- 처음에는 학부모가 연결된 학생 1~2명으로 먼저 시험하세요.
