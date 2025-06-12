# Python 3.10 기반 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# UV 설치 (빠른 Python 패키지 관리자)
RUN pip install uv

# 의존성 파일 복사
COPY requirements.txt pyproject.toml ./

# Python 의존성 설치
RUN uv pip install --system -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 저장된 스토리 디렉토리 생성 (권한 설정)
RUN mkdir -p saved_stories && chmod 755 saved_stories

# 포트 노출
EXPOSE 8501 8000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 시작 스크립트 복사 및 실행 권한 부여
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 기본 명령어 설정 (Streamlit 앱 실행)
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["streamlit"]
