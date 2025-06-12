"""
FastAPI 기반 스토리 편집 API 서버
"""
import json
import logging
import sys
import os
from typing import Dict, Any

# FastAPI 관련 import
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 프로젝트 모듈 import
try:
    from source.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
    from source.utils.prompts import get_system_prompt
    from source.utils.config import load_api_key
except ImportError as e:
    print(f"모듈 로드 실패: {e}")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="Story Edit API",
    description="AI 기반 스토리 편집 API",
    version="1.0.0"
)

# 전역 변수
llm_model = None
prompt_template = None

# 요청 모델 정의
class StoryEditRequest(BaseModel):
    chapterId: str
    story: str
    editRequest: str

class ScenarioResponse(BaseModel):
    chapterId: str
    story: str
    isCustom: bool

# 외부 백엔드 전송 기능 제거됨 - 클라이언트에게만 응답


def run_llm_for_edit(original_story: str, edit_request: str) -> str:
    """
    기존 스토리를 편집하여 새로운 시나리오 데이터를 생성합니다.
    
    Args:
        original_story (str): 편집할 원본 스토리 JSON 문자열
        edit_request (str): 편집 요청 사항
        
    Returns:
        str: 편집된 시나리오 JSON 문자열
    """
    global llm_model, prompt_template
    
    try:
        if not llm_model or not prompt_template:
            raise ValueError("LLM 모델이 초기화되지 않았습니다.")
        
        # 스토리 편집을 위한 시스템 프롬프트 생성
        story_edit_prompt = f"""당신은 10세 아동을 위한 투자 교육 스토리 편집 전문가입니다.

주요 역할:
1. 기존 스토리 데이터 분석 및 수정
2. 사용자 요청에 따른 특정 부분 편집 (캐릭터 이름, 이벤트, 대화)
3. 아동 친화적 언어 유지
4. 투자 교육 목적 보존
5. JSON 구조 일관성 유지

처리 범위:
✅ 스토리 내용 편집 (캐릭터, 이벤트, 대화)
✅ 난이도 조절 (쉽게/어렵게)
✅ 교육적 가치 강화
✅ 특정 턴의 상황, 뉴스 수정
✅ 캐릭터 이름 변경
❌ JSON 구조 변경 (7턴 유지 필수)
❌ 실제 투자 조언
❌ 기술적/프로그래밍 질문

편집 지침:
- 원본 스토리의 투자 교육 목적과 구조를 유지하세요
- 7턴의 게임 흐름을 그대로 유지하세요
- 각 턴의 turn_number, result, news, news_tag, stocks 구조를 유지하세요
- 요청된 부분만 수정하고 나머지는 최대한 원본을 유지하세요

원본 스토리:
{original_story}

편집 요청:
{edit_request}

위 편집 요청에 따라 원본 스토리를 수정하여 완전한 JSON 배열로 반환하세요.
반드시 다음과 같은 JSON 배열 형식으로 응답하세요:
[
  {{
    "turn_number": 1,
    "result": "게임 상황 설명",
    "news": "관련 뉴스나 이벤트",
    "news_tag": "all",
    "stocks": [
      {{
        "name": "상점/캐릭터 이름",
        "risk_level": "위험도 설명",
        "description": "상점 설명",
        "before_value": 100,
        "current_value": 100,
        "expectation": "기대/전망"
      }}
    ]
  }}
]"""
        
        # LLM을 통해 스토리 편집
        result = generate_game_data(llm_model, prompt_template, story_edit_prompt)
        
        if not result:
            raise ValueError("LLM에서 유효한 응답을 생성하지 못했습니다.")
        
        return result
        
    except Exception as e:
        logger.error(f"LLM 스토리 편집 중 오류: {e}")
        raise


def determine_chapter_id(story_content: str) -> str:
    """
    스토리 내용을 분석하여 적절한 chapterId를 결정합니다.
    
    Args:
        story_content (str): 생성된 스토리 내용
        
    Returns:
        str: 해당하는 chapterId
    """
    # 시나리오 타입별 chapterId 매핑
    CHAPTER_ID_MAPPING = {
        "three_little_pigs": "1111",
        "아기돼지": "1111",
        "아기 돼지": "1111",
        "돼지": "1111",
        "foodtruck": "2222",
        "푸드트럭": "2222",
        "magic_kingdom": "3333",
        "마법왕국": "3333",
        "마법 왕국": "3333",
        "moonlight_thief": "4444",
        "달빛도둑": "4444",
        "달빛 도둑": "4444"
    }
    
    story_lower = story_content.lower()
    
    # 키워드 기반으로 chapterId 결정
    for keyword, chapter_id in CHAPTER_ID_MAPPING.items():
        if keyword.lower() in story_lower:
            return chapter_id
    
    # 기본값: 달빛 도둑 (4444)
    return "4444"


# send_to_backend 함수 제거됨 - 클라이언트 응답만 제공


@app.on_event("startup")
async def startup_event():
    """앱 시작시 초기화"""
    global llm_model, prompt_template
    
    try:
        # API 키 확인
        api_key = load_api_key()
        if not api_key:
            logger.error("Google API 키가 설정되지 않았습니다.")
            raise ValueError("Google API 키가 설정되지 않았습니다.")
        
        # LLM 모델 초기화
        logger.info("LLM 모델 초기화 중...")
        llm_model = initialize_llm()
        
        # 프롬프트 템플릿 생성
        system_prompt = get_system_prompt()
        prompt_template = create_prompt_template(system_prompt)
        
        logger.info("FastAPI 서버 초기화 완료")
        
    except Exception as e:
        logger.error(f"서버 초기화 실패: {e}")
        raise


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Story Edit API Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    global llm_model, prompt_template
    
    return {
        "status": "healthy",
        "llm_initialized": llm_model is not None,
        "prompt_template_ready": prompt_template is not None
    }


@app.post("/edit-scenario", response_model=ScenarioResponse)
async def edit_scenario(request: StoryEditRequest):
    """
    기존 스토리 편집 엔드포인트
    
    Args:
        request: 스토리 편집 요청 데이터 (chapterId, story, editRequest)
        
    Returns:
        ScenarioResponse: 편집된 시나리오 응답
    """
    try:
        logger.info(f"스토리 편집 요청 받음 - chapterId: {request.chapterId}, 편집 요청: {request.editRequest[:100]}...")
        
        # 입력 검증
        if not request.chapterId or not request.chapterId.strip():
            raise HTTPException(status_code=400, detail="chapterId는 비어있을 수 없습니다.")
        
        if not request.story or not request.story.strip():
            raise HTTPException(status_code=400, detail="원본 스토리는 비어있을 수 없습니다.")
            
        if not request.editRequest or not request.editRequest.strip():
            raise HTTPException(status_code=400, detail="편집 요청은 비어있을 수 없습니다.")
        
        # 원본 스토리 JSON 유효성 검증
        try:
            original_story_data = json.loads(request.story)
            if not isinstance(original_story_data, list):
                raise ValueError("원본 스토리 데이터는 배열 형태여야 합니다.")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="원본 스토리가 유효한 JSON 형식이 아닙니다.")
        
        # LLM을 통해 스토리 편집
        logger.info("LLM을 통한 스토리 편집 시작...")
        edited_story_json = run_llm_for_edit(request.story, request.editRequest.strip())
        
        if not edited_story_json:
            raise HTTPException(status_code=500, detail="스토리 편집에 실패했습니다.")
        
        # 편집된 스토리 JSON 유효성 검증
        try:
            edited_story_data = json.loads(edited_story_json)
            if not isinstance(edited_story_data, list):
                raise ValueError("편집된 스토리 데이터는 배열 형태여야 합니다.")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="편집된 시나리오가 유효한 JSON 형식이 아닙니다.")
        
        # 응답 데이터 구성 (한글 보존, 기존 chapterId 유지)
        scenario_response_data = {
            "chapterId": request.chapterId.strip(),
            "story": json.dumps(edited_story_data, ensure_ascii=False, separators=(',', ':')),
            "isCustom": True
        }
        
        logger.info(f"스토리 편집 완료 - chapterId: {request.chapterId}")
        
        # 클라이언트에 응답 반환
        return ScenarioResponse(**scenario_response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"스토리 편집 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")


if __name__ == "__main__":
    # 개발용 서버 실행
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
