# 🎮 AI 스토리 편집 챗봇

Google Gemini AI와 함께 기존 투자 교육 스토리를 편집하고 개선할 수 있는 Streamlit 앱입니다.
저장된 투자 교육 게임 스토리를 선택하여 AI와 자연어 대화로 내용을 수정할 수 있습니다.

## ✨ 주요 기능

- **📚 스토리 파일 인식**: `saved_stories` 폴더의 JSON 파일 자동 인식 및 로드
- **💬 자연어 편집**: "3턴 이벤트를 더 재미있게 만들어줘" 같은 자연어 요청으로 편집
- **🎭 세밀한 편집**: 캐릭터, 배경, 이벤트, 대화 등 요소별 맞춤 수정
- **🔍 실시간 검증**: 수정된 스토리의 구조와 품질 자동 검증
- **📊 편집 분석**: 사용자 의도 분석 및 개선 제안 제공
- **🎯 교육적 가치**: 10세 이하 아동을 위한 투자 교육 게임에 최적화

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd making_story_chatbot

# Google Gemini API 키 설정
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

### 2. 의존성 설치 및 실행

**UV 사용 (권장):**
```bash
# UV 설치 (미설치시)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 실행 스크립트 사용
chmod +x run_app.sh
./run_app.sh

# 또는 직접 실행
uv run streamlit run app.py
```

**일반 Python 환경:**
```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

### 3. 브라우저에서 접속

앱이 실행되면 자동으로 브라우저가 열리거나 `http://localhost:8501`로 접속하세요.

## 📁 프로젝트 구조

```
making_story_chatbot/
├── 📱 app.py                        # 메인 Streamlit 앱
├── 📋 requirements.txt              # Python 패키지 의존성
├── ⚙️  pyproject.toml               # UV 프로젝트 설정
├── 🚀 run_app.sh                    # 실행 스크립트
├── 🔐 .env                          # 환경 변수 (생성 필요)
├── 📝 README.md                     # 프로젝트 문서
├── 🧪 test_story_modification.py    # 테스트 스크립트
├── ✅ final_verification.py         # 최종 검증 스크립트
├── 📂 source/                       # 소스 코드
│   ├── 🔧 components/
│   │   ├── game_customizer.py      # 🎯 스토리 편집 핵심 로직
│   │   └── story_editor.py         # 📝 스토리 편집 도우미
│   ├── 🤖 models/
│   │   └── llm_handler.py          # Google Gemini API 처리
│   ├── 🎨 ui/
│   │   ├── sidebar.py              # 사이드바 (편집 가이드)
│   │   ├── story_selector.py       # 스토리 선택기
│   │   ├── chat_interface.py       # 💬 AI 편집 채팅 인터페이스
│   │   ├── story_viewer.py         # 스토리 미리보기
│   │   └── info_tabs.py            # 정보 및 가이드 탭
│   └── 🛠️ utils/
│       ├── config.py               # API 설정
│       ├── prompts.py              # 편집용 프롬프트
│       ├── story_manager.py        # 📁 스토리 파일 관리
│       └── chatbot_helper.py       # 🤖 챗봇 도우미 기능
└── 📚 saved_stories/               # 편집 대상 스토리 파일들
    ├── game_scenario_magic_kingdom_*.json     # 🏰 마법왕국 스토리
    ├── game_scenario_foodtruck_kingdom_*.json # 🚚 푸드트럭 스토리
    ├── game_scenario_moonlight_thief_*.json   # 🌙 달빛도둑 스토리
    └── game_scenario_three_little_pigs_*.json # 🐷 아기돼지 삼형제 스토리
```

## 🎯 사용 방법

### 1. 스토리 선택 및 로드
1. 메인 페이지에서 편집하고 싶은 스토리를 선택
2. "📖 불러오기" 버튼을 클릭하여 스토리 로드
3. 스토리가 성공적으로 로드되면 편집 모드로 전환

### 2. AI와 대화로 스토리 편집
편집 인터페이스에서 자연어로 요청하세요:

**캐릭터 수정:**
- "주인공의 이름을 민수로 바꿔줘"
- "악역을 더 매력적으로 만들어줘"

**이벤트 수정:**
- "3턴 이벤트를 더 재미있게 만들어줘"
- "마법 요소를 추가해줘"

**배경 수정:**
- "배경을 우주로 바꿔줘"
- "더 신비로운 분위기로 만들어줘"

**대화 수정:**
- "대화를 더 재미있게 수정해줘"
- "아이들이 이해하기 쉽게 바꿔줘"

### 3. 결과 확인 및 품질 검증
- ✨ AI가 의도를 분석하고 적절한 수정 적용
- 📊 실시간으로 수정된 게임 턴 수 표시
- ✅ 자동 품질 검증 및 이슈 보고
- 💡 추가 개선 제안 제공

## 🔧 주요 특징

### ✅ 해결된 문제들
- **파일 인식 오류**: `saved_stories` 폴더의 모든 JSON 파일 형식 자동 인식
- **데이터 검증**: `turn_number` 필드 기반의 정확한 구조 검증
- **품질 보증**: 수정된 스토리의 교육적 가치 및 아동 적합성 자동 검증
- **자연어 처리**: "3턴 이벤트를 더 재미있게 만들어줘" 같은 구체적 요청 처리

### 🤖 AI 기능
- **의도 분석**: 사용자 요청을 캐릭터/설정/이벤트/대화 수정으로 분류
- **컨텍스트 관리**: 이전 대화 내용을 바탕으로 일관된 편집
- **품질 검증**: LLM 응답의 JSON 형식, 필수 필드, 내용 적절성 검증
- **개선 제안**: 추가적인 편집 아이디어 자동 제안

### 📊 스토리 데이터 형식
```json
[
  {
    "turn_number": 1,
    "result": "게임 진행 상황 설명",
    "news": "해당 턴의 뉴스/이벤트",
    "news_tag": "이벤트 영향 범위",
    "stocks": [
      {
        "name": "투자 옵션 이름",
        "description": "상세 설명",
        "before_value": 100,
        "current_value": 105,
        "risk_level": "저위험|중위험|고위험",
        "expectation": "다음 턴 예상"
      }
    ]
  }
]
```

## 🚀 개발 및 테스트

### 테스트 실행
```bash
# 기본 기능 테스트
python test_story_modification.py

# 최종 검증 테스트
python final_verification.py
```

### 개발 환경 설정
```bash
# 개발용 의존성 설치
uv add --dev pytest black flake8

# 코드 포맷팅
uv run black source/
uv run flake8 source/
```

## 🔧 문제 해결

### API 관련 문제
```bash
# API 키 확인
echo $GOOGLE_API_KEY

# .env 파일 확인
cat .env
```

### 스토리 파일 문제
- 파일명 형식: `game_scenario_{type}_{timestamp}.json`
- 지원 타입: `magic_kingdom`, `foodtruck_kingdom`, `moonlight_thief`, `three_little_pigs`
- 디버깅: 에러 발생 시 "🔧 디버깅 정보" 펼치기로 상세 정보 확인

### 성능 최적화
- 대화 기록이 길어지면 "💬 대화 초기화" 버튼으로 리셋
- 큰 스토리 파일의 경우 편집 범위를 특정 턴으로 제한
- 브라우저 캐시 문제 시 하드 리프레시 (Ctrl+Shift+R)

## 📋 업데이트 로그

### v1.0.0 - 스토리 편집 챗봇 완성 ✅
- **핵심 기능 구현**: Google Gemini API 기반 스토리 편집
- **파일 호환성**: 기존 JSON 배열 형식과 새로운 메타데이터 형식 모두 지원
- **사용성 개선**: 자연어 편집 요청, 실시간 품질 검증, 디버깅 정보 제공
- **안정성 확보**: 에러 처리 강화, 세션 관리 개선

### 수정된 주요 컴포넌트
- `source/components/game_customizer.py`: 편집 핵심 로직
- `source/components/story_editor.py`: 파일 로딩 및 검증
- `source/utils/story_manager.py`: 파일 인식 개선
- `source/utils/chatbot_helper.py`: 스토리 편집 특화
- `source/ui/chat_interface.py`: 사용자 경험 개선

## 📞 지원

프로젝트 관련 문의나 버그 리포트는 이슈를 생성해주세요.

---
**Made with ❤️ using Google Gemini AI and Streamlit**
- `source/ui/sidebar.py`: 편집 팁과 시스템 상태만 표시하도록 간소화
- `source/models/llm_handler.py`: Google Gemini API 통합
- `source/utils/config.py`: Google API 키 설정으로 변경

## 📝 라이선스

MIT License

## 🤝 기여하기

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제나 질문이 있으시면 GitHub Issues에서 이슈를 생성해주세요.

---

**⚡ 빠른 시작**: `./run_app.sh` 실행 후 브라우저에서 `http://localhost:8501` 접속  
**🔑 필수 설정**: `.env` 파일에 `GOOGLE_API_KEY` 설정 필요
