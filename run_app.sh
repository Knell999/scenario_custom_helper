#!/bin/bash

echo "🚀 UV 가상환경을 사용하여 Streamlit 앱 실행 중..."

# UV가 설치되어 있는지 확인
if ! command -v uv &> /dev/null; then
    echo "❌ UV가 설치되어 있지 않습니다. 다음 명령으로 설치해주세요:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV 발견됨"

# 가상환경이 없으면 생성
if [ ! -d ".venv" ]; then
    echo "📦 가상환경 생성 중..."
    uv venv
fi

# 필요한 패키지 설치 (이미 설치되어 있으면 스킵됨)
echo "📦 패키지 의존성 확인 중..."
uv pip install streamlit langchain langchain-google-genai python-dotenv google-generativeai

# .env 파일 존재 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. GOOGLE_API_KEY를 설정해주세요."
    echo "예시: echo 'GOOGLE_API_KEY=your_api_key_here' > .env"
fi

# Streamlit 앱 실행
echo "🎮 Streamlit 앱 시작 중..."
source .venv/bin/activate && streamlit run app.py
