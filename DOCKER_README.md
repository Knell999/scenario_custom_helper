# Docker 사용 가이드

## 📦 Docker로 애플리케이션 실행하기

### 1. 환경 변수 설정

먼저 Google API 키를 환경 변수로 설정해야 합니다:

```bash
# .env 파일 생성
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env
```

### 2. Docker로 빌드 및 실행

#### Option A: Docker Compose 사용 (권장)

```bash
# Streamlit 앱만 실행
docker-compose up --build

# 백그라운드에서 실행
docker-compose up -d --build

# FastAPI 서버만 실행
docker-compose --profile api-only up --build

# 정지
docker-compose down
```

#### Option B: Docker 직접 사용

```bash
# 이미지 빌드
docker build -t making-story-chatbot .

# Streamlit 앱 실행
docker run -d \
  --name story-chatbot \
  -p 8501:8501 \
  -e GOOGLE_API_KEY=your_api_key \
  -v $(pwd)/saved_stories:/app/saved_stories \
  making-story-chatbot

# FastAPI 서버 실행
docker run -d \
  --name story-api \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_api_key \
  -v $(pwd)/saved_stories:/app/saved_stories \
  making-story-chatbot fastapi

# 두 서비스 모두 실행
docker run -d \
  --name story-full \
  -p 8501:8501 \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_api_key \
  -v $(pwd)/saved_stories:/app/saved_stories \
  making-story-chatbot both
```

### 3. 접속

- **Streamlit 앱**: http://localhost:8501
- **FastAPI 서버**: http://localhost:8000
- **FastAPI 문서**: http://localhost:8000/docs

### 4. 컨테이너 관리

```bash
# 실행 중인 컨테이너 확인
docker ps

# 로그 확인
docker logs story-chatbot

# 컨테이너 접속
docker exec -it story-chatbot bash

# 컨테이너 중지
docker stop story-chatbot

# 컨테이너 제거
docker rm story-chatbot

# 이미지 제거
docker rmi making-story-chatbot
```

### 5. 개발 모드

개발 중에 코드 변경사항을 실시간으로 반영하려면:

```bash
# docker-compose.yml에서 volumes 섹션의 주석을 해제하고 실행
docker-compose up --build
```

### 6. 문제 해결

#### 권한 문제
```bash
# saved_stories 디렉토리 권한 확인
ls -la saved_stories/

# 권한 수정
chmod 755 saved_stories/
```

#### 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :8501
lsof -i :8000

# 다른 포트 사용
docker run -p 8502:8501 making-story-chatbot
```

#### 메모리 부족
```bash
# 메모리 제한 설정
docker run --memory="1g" making-story-chatbot
```

### 7. 환경 변수 옵션

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `GOOGLE_API_KEY` | Google Gemini API 키 | 필수 |
| `STREAMLIT_SERVER_PORT` | Streamlit 포트 | 8501 |
| `FASTAPI_PORT` | FastAPI 포트 | 8000 |

### 8. 배포 시 주의사항

- `GOOGLE_API_KEY`를 안전하게 관리하세요
- 프로덕션에서는 `.env` 파일 대신 환경 변수를 직접 설정하세요
- 볼륨 마운트로 데이터 영속성을 확보하세요
- 헬스체크를 통해 서비스 상태를 모니터링하세요

### 9. 로그 수집

```bash
# 모든 로그 보기
docker-compose logs

# 특정 서비스 로그
docker-compose logs story-chatbot

# 실시간 로그 스트리밍
docker-compose logs -f
```
