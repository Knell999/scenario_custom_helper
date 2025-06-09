# 💰 투자 교육 스토리 챗봇

AI 챗봇과 대화하여 아이들을 위한 투자 교육 게임 스토리를 커스터마이징할 수 있는 Streamlit 앱입니다. 
게임을 통해 안정형 투자, 분산투자, 매매 타이밍, 성장형 투자 등의 기본 개념을 학습할 수 있습니다.

## ✨ 주요 기능

- **💰 투자 교육 중심**: 안정형 투자, 분산투자, 매매 타이밍, 성장형 투자 학습
- **🤖 AI 챗봇 대화**: 자연어로 투자 학습 목표에 맞는 스토리 변경 요청
- **🎭 다양한 시나리오**: 마법 왕국, 푸드트럭 왕국, 달빛 도둑 등
- **🎯 난이도 조절**: 학습자 수준에 맞는 쉬움/보통/어려움 설정
- **🧠 지능형 의도 분석**: 투자 학습 의도를 자동으로 분석하여 최적화된 응답 제공
- **💾 스토리 저장/관리**: 생성한 투자 교육 스토리를 저장하고 불러오기
- **📚 투자 가이드**: 실시간 투자 교육 팁과 가이드 제공

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

## 📁 프로젝트 구조

```
making_story_chatbot/
├── app.py                    # 메인 Streamlit 앱 (모듈화됨)
├── requirements.txt          # 패키지 의존성
├── pyproject.toml           # UV 프로젝트 설정
├── run_app.sh               # 실행 스크립트
├── .env                     # 환경 변수 (생성 필요)
├── source/
│   ├── components/
│   │   ├── __init__.py
│   │   └── game_customizer.py # 게임 커스터마이징 로직
│   ├── models/
│   │   ├── __init__.py
│   │   └── llm_handler.py   # LLM 처리 로직
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── sidebar.py       # 투자 학습 설정 사이드바
│   │   ├── chat_interface.py # 챗봇 대화 인터페이스
│   │   ├── story_viewer.py  # 스토리 뷰어
│   │   └── info_tabs.py     # 정보 및 팁 탭
│   └── utils/
│       ├── __init__.py
│       ├── config.py        # 설정 관리
│       ├── prompts.py       # 프롬프트 템플릿
│       ├── chatbot_helper.py # 투자 교육 의도 분석
│       └── story_manager.py # 스토리 저장/관리
└── saved_stories/          # 저장된 스토리 (자동 생성)
```

## 🎯 사용 방법

1. **투자 학습 목표 선택**: 사이드바에서 학습하고 싶은 투자 방식 선택
   - 안정형 투자 (리스크 관리, 안전한 투자)
   - 분산투자 (포트폴리오 구성, 리스크 분산)
   - 매매 타이밍 (시장 타이밍, 정기 투자)
   - 성장형 투자 (고수익 추구, 성장 가능성)

2. **난이도 설정**: 학습자 수준에 맞는 난이도 선택 (쉬움/보통/어려움)

3. **시나리오 선택**: 원하는 기본 시나리오 선택

4. **챗봇과 대화**: 투자 학습 목표에 맞는 변경사항을 자연어로 입력

5. **스토리 확인**: 생성된 투자 교육 스토리 미리보기

6. **저장/다운로드**: 마음에 드는 교육 스토리 저장

## 💡 투자 교육 커스터마이징 예시

### 안정형 투자 학습
- "안전한 투자가 왜 중요한지 알려줘"
- "리스크를 줄이는 방법을 게임으로 보여줘"
- "예금과 적금의 차이를 스토리로 설명해줘"

### 분산투자 학습
- "계란을 한 바구니에 담지 말라는 말을 게임으로 표현해줘"
- "여러 가지 투자 상품을 조합하는 방법을 알려줘"
- "포트폴리오 구성의 기본을 배우고 싶어"

### 매매 타이밍 학습
- "언제 사고 팔아야 하는지 알려줘"
- "감정적으로 투자하면 안 되는 이유를 보여줘"
- "정기 투자의 장점을 스토리로 설명해줘"

### 성장형 투자 학습
- "더 높은 수익을 얻는 방법을 알려줘"
- "기업의 성장 가능성을 판단하는 방법"
- "장기 투자의 중요성을 배우고 싶어"

### 난이도 조절
- "더 쉬운 단어로 설명해줘"
- "초등학생도 이해할 수 있게 해줘"
- "더 복잡한 투자 개념을 포함해줘"

## 🔧 고급 설정

### 모델 설정 변경
`source/utils/config.py`에서 GPT 모델 및 매개변수를 조정할 수 있습니다:

```python
def get_model_settings():
    return {
        "model_name": "gpt-4o-mini",  # 모델 변경
        "temperature": 1.05,          # 창의성 조절
        "max_tokens": 4096           # 최대 토큰 수
    }
```

### 저장 위치 변경
기본적으로 `saved_stories` 폴더에 저장되며, `StoryManager` 클래스 초기화 시 변경 가능합니다.

## 🐛 문제 해결

### API 키 오류
- `.env` 파일에 올바른 Google API 키가 설정되어 있는지 확인
- API 키에 충분한 크레딧이 있는지 확인

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

## 📝 라이선스

MIT License

## 🤝 기여하기

1. Fork the project
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 지원

문제나 질문이 있으시면 이슈를 생성해주세요.
