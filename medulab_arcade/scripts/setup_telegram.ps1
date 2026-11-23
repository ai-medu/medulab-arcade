# 텔레그램 알림 설정: 봇 토큰을 직접 입력하면 채팅 ID를 찾아 서버에 저장하고 테스트 메시지를 보냅니다.
# 토큰은 화면에 보이지 않으며 이 컴퓨터와 서버 설정 파일에만 저장됩니다.
$ErrorActionPreference = 'Stop'
$secure = Read-Host '봇 토큰을 붙여넣고 Enter (화면에 표시되지 않습니다)' -AsSecureString
$token = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)).Trim()
if ($token -notmatch '^\d+:[A-Za-z0-9_-]{30,}$') { Write-Host '토큰 형태가 올바르지 않습니다. 다시 실행해 주세요.'; exit 1 }

$updates = Invoke-RestMethod "https://api.telegram.org/bot$token/getUpdates"
$chat = $updates.result | Where-Object { $_.message } | Select-Object -Last 1
if (-not $chat) { Write-Host '봇에게 보낸 메시지가 없습니다. 텔레그램에서 봇을 열어 시작(Start)을 누르고 아무 말이나 보낸 뒤 다시 실행해 주세요.'; exit 1 }
$chatId = $chat.message.chat.id
Write-Host "채팅 확인됨: $($chat.message.chat.first_name) (ID $chatId)"

$remote = "cd ~/medulab_arcade/medulab_arcade && sed -i '/^TELEGRAM_/d' .env && printf '\nTELEGRAM_BOT_TOKEN=%s\nTELEGRAM_CHAT_IDS=%s\n' '$token' '$chatId' >> .env && sudo -n systemctl restart medulab && systemctl is-active medulab"
ssh -i D:/ssh/id_ed25519_claude deploy@64.176.227.66 $remote

Invoke-RestMethod "https://api.telegram.org/bot$token/sendMessage" -Method Post -ContentType 'application/json' `
    -Body ([Text.Encoding]::UTF8.GetBytes((@{ chat_id = $chatId; text = '✅ 메듀랩 알림 연결 완료! 새 상담 문의, 특강 예약, 결석 사유, 신규 가입이 생기면 여기로 알려드릴게요.' } | ConvertTo-Json))) | Out-Null
Write-Host '완료! 텔레그램에서 테스트 메시지를 확인하세요.'
