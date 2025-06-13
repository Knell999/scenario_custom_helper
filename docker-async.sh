#!/bin/bash

# Docker 빌드 및 실행 스크립트 (비동기 처리 지원)

set -e

echo "🐳 비동기 처리 지원 Docker 빌드 및 실행 스크립트"
echo "=============================================="

# 함수 정의
build_image() {
    echo "🔨 Docker 이미지 빌드 중..."
    docker build -t story-chatbot-async:latest .
    echo "✅ 빌드 완료"
}

run_fastapi_only() {
    echo "🚀 FastAPI 서버만 실행 (비동기 처리 지원)"
    docker run -d \
        --name story-api-async \
        -p 8000:8000 \
        -e GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
        -e UVICORN_LOOP=asyncio \
        -e ASYNC_SUPPORT=true \
        -v "$(pwd)/saved_stories:/app/saved_stories" \
        -v "$(pwd)/logs:/app/logs" \
        story-chatbot-async:latest fastapi
    
    echo "✅ FastAPI 서버 시작됨 (포트: 8000)"
    echo "🔗 엔드포인트:"
    echo "   - http://localhost:8000"
    echo "   - http://localhost:8000/health"
    echo "   - http://localhost:8000/async-status"
}

run_with_compose() {
    echo "🚀 Docker Compose로 전체 시스템 실행"
    docker-compose up -d
    echo "✅ 시스템 시작됨"
    echo "🔗 접속 URL:"
    echo "   - Streamlit: http://localhost:8501"
    echo "   - FastAPI: http://localhost:8000"
}

test_async_endpoints() {
    echo "🧪 비동기 엔드포인트 테스트"
    
    # 서버가 준비될 때까지 대기
    echo "⏳ 서버 준비 대기 중..."
    sleep 10
    
    echo "📊 헬스체크 테스트:"
    curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ 헬스체크 실패"
    
    echo -e "\n📊 비동기 상태 테스트:"
    curl -s http://localhost:8000/async-status | python3 -m json.tool || echo "❌ 비동기 상태 확인 실패"
}

stop_containers() {
    echo "🛑 컨테이너 중지 및 정리"
    docker stop story-api-async 2>/dev/null || true
    docker rm story-api-async 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    echo "✅ 정리 완료"
}

show_help() {
    echo "사용법: $0 [command]"
    echo ""
    echo "명령어:"
    echo "  build       Docker 이미지 빌드"
    echo "  fastapi     FastAPI 서버만 실행"
    echo "  compose     Docker Compose로 전체 시스템 실행"
    echo "  test        비동기 엔드포인트 테스트"
    echo "  stop        모든 컨테이너 중지"
    echo "  help        이 도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 build && $0 fastapi"
    echo "  $0 compose"
    echo "  $0 test"
}

# 메인 로직
case "${1:-help}" in
    "build")
        build_image
        ;;
    "fastapi")
        stop_containers
        run_fastapi_only
        ;;
    "compose")
        stop_containers
        run_with_compose
        ;;
    "test")
        test_async_endpoints
        ;;
    "stop")
        stop_containers
        ;;
    "help"|*)
        show_help
        ;;
esac
