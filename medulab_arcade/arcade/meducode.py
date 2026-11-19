"""메듀코드(블록코딩 도구) 서비스.

메듀코드는 별도 프로젝트(React + Vite)로 개발하고, 빌드 결과(dist)만 서버의 MEDUCODE_DIST 폴더에 복사해 둔다.
이 뷰가 /meducode/ 아래에서 그 파일들을 그대로 내려 준다. (메듀랩과 같은 서버·같은 도메인이라 로그인 연동도 쉽다)
"""
import os

from django.conf import settings
from django.http import Http404
from django.views.static import serve


def meducode_app(request, path=''):
    root = settings.MEDUCODE_DIST
    if not os.path.isdir(root):
        raise Http404('메듀코드가 아직 준비되지 않았어요.')
    path = path or 'index.html'
    response = serve(request, path, document_root=root)
    if path == 'index.html':
        response['Cache-Control'] = 'no-cache'   # 새로 배포하면 바로 최신 화면을 받도록
    elif path.startswith('assets/'):
        response['Cache-Control'] = 'public, max-age=31536000, immutable'   # 파일 이름에 해시가 붙어 있어 안전
    else:
        response['Cache-Control'] = 'public, max-age=3600'
    return response
