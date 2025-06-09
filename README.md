# 🎮 투자 교육 스토리 편집기

Google Gemini AI와 함께 기존 투자 교육 스토리를 편집하고 개선할 수 있는 Streamlit 앱입니다.
저장된 투자 교육 게임 스토리를 선택하여 AI와 대화하며 내용을 수정할 수 있습니다.

## ✨ 주요 기능

- **✏️ 스토리 편집 전용**: 기존 저장된 스토리만 편집 가능 (새 생성 기능 없음)
- **🤖 AI 편집 도우미**: Google Gemini와 자연어 대화로 스토리 수정
- **🎭 다양한 편집 옵션**: 캐릭터, 배경, 이벤트, 대화 등 세부 편집
- **📊 실시간 미리보기**: 편집 내용을 즉시 확인
- **💾 스토리 관리**: 저장된 스토리 불러오기/삭제
- **🔍 스토리 분석**: 편집 의도 자동 분석 및 품질 검증
- **🎯 투자 교육 특화**: 투자 개념과 게임 스토리의 완벽한 결합

## 🚀 빠른 시작 (UV 환경)

### 1. 환경 설정

```bash
# UV 설치 (미설치시)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 클론 또는 다운로드 후 디렉토리 이동
cd making_story_chatbot

# Google API 키 설정
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### 2. 앱 실행

```bash
# 실행 스크립트 사용 (권장)
./run_app.sh

# 또는 직접 실행
uv add streamlit langchain langchain-google-genai python-dotenv google-generativeai
uv run streamlit run app.py
```

### 3. 브라우저에서 접속

앱이 실행되면 브라우저에서 `http://localhost:8501`로 접속하세요.
(포트 충돌 시 자동으로 다른 포트 사용)

## 📁 프로젝트 구조

```
making_story_chatbot/
├── app.py                     # 메인 Streamlit 앱
├── requirements.txt           # 패키지 의존성 
├── pyproject.toml            # UV 프로젝트 설정
├── run_app.sh                # 실행 스크립트
├── .env                      # 환경 변수 (생성 필요)
├── source/
│   ├── components/
│   │   ├── game_customizer.py    # 스토리 편집 로직
│   │   └── story_editor.py       # 스토리 편집 도우미
│   ├── models/
│   │   └── llm_handler.py        # Google Gemini API 처리
│   ├── ui/
│   │   ├── sidebar.py            # 간소화된 사이드바 (편집 팁)
│   │   ├── story_selector.py     # 메인 페이지 스토리 선택기
│   │   ├── chat_interface.py     # AI 편집 채팅 인터페이스
│   │   ├── story_viewer.py       # 스토리 미리보기
│   │   └── info_tabs.py          # 정보 및 가이드 탭
│   └── utils/
│       ├── config.py             # Google Gemini API 설정
│       ├── prompts.py            # 편집용 프롬프트
│       └── story_manager.py      # 스토리 파일 관리
└── saved_stories/               # 편집 대상 스토리 파일들
    ├── magic_kingdom*.json      # 마법왕국 스토리들
    ├── food_truck*.json         # 푸드트럭 스토리들  
    └── moonlight.json           # 달빛도둑 스토리
```

## 🎯 사용 방법

### 1. 스토리 선택
- 메인 페이지에서 편집하고 싶은 스토리를 선택
- 현재 이용 가능한 스토리:
  - 🏰 **마법왕국** 스토리들
  - 🚚 **푸드트럭** 스토리들
  - 🌙 **달빛도둑** 스토리

### 2. 스토리 편집
- AI 채팅 인터페이스를 통해 자연어로 편집 요청
- 실시간으로 변경사항을 미리보기에서 확인
- 다양한 편집 옵션 활용

### 3. 편집 완료
- 만족스러운 결과가 나오면 스토리 저장
- 필요시 백업 파일 생성

## 💡 스토리 편집 예시

### 캐릭터 수정
- "주인공의 이름을 민수로 바꿔줘"
- "악역 캐릭터를 더 매력적으로 만들어줘"
- "새로운 조력자를 추가해줘"

### 배경 및 설정 변경
- "배경을 현대 도시로 바꿔줘"
- "판타지 요소를 더 추가해줘"
- "현실적인 투자 상황으로 바꿔줘"

### 투자 교육 요소 강화
- "리스크 관리에 대한 내용을 더 자세히 설명해줘"
- "분산투자의 중요성을 스토리에 자연스럽게 녹여줘"
- "복리 효과를 게임 요소로 표현해줘"

### 난이도 조절
- "초보자도 이해하기 쉽게 설명해줘"
- "더 복잡한 투자 개념을 포함해줘"
- "게임 요소를 더 강화해줘"

## 🔧 고급 설정

### 모델 설정 변경
`source/utils/config.py`에서 Google Gemini 모델 및 매개변수를 조정할 수 있습니다:

```python
def get_model_settings():
    return {
        "model_name": "gemini-2.5-flash-preview-05-20",  # 모델 변경
        "temperature": 1,                                 # 창의성 조절
        "max_tokens": 4096                               # 최대 토큰 수
    }
```

### 저장 위치 변경
기본적으로 `saved_stories` 폴더에 저장되며, `StoryManager` 클래스 초기화 시 변경 가능합니다.

### UI 커스터마이징
- `source/ui/` 폴더의 각 컴포넌트를 수정하여 인터페이스 변경 가능
- `story_selector.py`: 메인 페이지 스토리 선택 화면
- `chat_interface.py`: AI 채팅 편집 인터페이스
- `story_viewer.py`: 스토리 미리보기 화면
- `sidebar.py`: 사이드바 (편집 팁 및 시스템 상태)

## 🐛 문제 해결

### API 키 오류
- `.env` 파일에 올바른 Google API 키가 설정되어 있는지 확인
- Google AI Studio에서 API 키를 생성했는지 확인
- API 키에 충분한 할당량이 있는지 확인

### 패키지 설치 오류
```bash
# UV 재설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 캐시 클리어 후 재설치
uv cache clean
uv add streamlit langchain langchain-google-genai python-dotenv google-generativeai
```

### 포트 충돌
다른 포트에서 실행하려면:
```bash
uv run streamlit run app.py --server.port 8502
```

### 스토리 파일 오류
- `saved_stories` 폴더에 JSON 파일이 올바른 형식인지 확인
- 백업 파일들이 있는 경우 원본 파일 복원 시도

### 성능 문제
- 너무 긴 스토리의 경우 편집 속도가 느려질 수 있음
- 대화 기록이 많아지면 메모리 사용량 증가
- 필요시 브라우저 새로고침으로 세션 초기화

## 📋 주요 변경사항

### v2.0 - Google Gemini 전환 및 UI 개편
- **API 변경**: OpenAI → Google Gemini API (gemini-2.5-flash-preview-05-20)
- **UI 재구성**: 스토리 선택기를 메인 페이지로 이동, 중복 제거
- **편집 전용**: 새 스토리 생성 기능 제거, 기존 스토리 편집에 집중
- **성능 개선**: 더 빠른 응답 속도와 안정적인 편집 경험

### 주요 파일 구조 변경
- `app.py`: 조건부 렌더링으로 워크플로우 개선
- `source/ui/story_selector.py`: 새로운 메인 페이지 스토리 선택 컴포넌트
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
