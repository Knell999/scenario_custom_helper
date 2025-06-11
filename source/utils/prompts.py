"""
프롬프트 관리 모듈 - 스토리 편집 전용
"""

def get_system_prompt():
    """스토리 편집을 위한 시스템 프롬프트"""
    return """당신은 10세 아동을 위한 투자 교육 스토리 편집 전문가입니다.

주요 역할:
1. 기존 스토리 데이터 분석 및 수정
2. 사용자 요청에 따른 특정 부분 편집 (캐릭터, 배경, 이벤트, 대화)
3. 아동 친화적 언어 유지
4. 투자 교육 목적 보존
5. JSON 구조 일관성 유지

처리 범위:
✅ 스토리 내용 편집 (캐릭터, 배경, 이벤트, 대화)
✅ 난이도 조절 (쉽게/어렵게)
✅ 교육적 가치 강화
❌ 새로운 게임 생성 (편집만 지원)
❌ 실제 투자 조언
❌ 기술적/프로그래밍 질문

중요: 수정된 전체 스토리를 유효한 JSON 형식으로만 반환하세요."""

def get_story_modification_prompt(original_story_data, user_request, modification_type="general"):
    """
    기존 스토리 수정을 위한 프롬프트를 반환합니다.
    
    Args:
        original_story_data (str): 원본 스토리 데이터 (JSON 문자열)
        user_request (str): 사용자의 수정 요청
        modification_type (str): 수정 유형 ("character", "setting", "events", "dialogue", "general")
        
    Returns:
        str: 스토리 수정 프롬프트
    """
    modification_instructions = {
        "character": "캐릭터의 이름, 성격, 외모, 대사 등을 수정하세요.",
        "setting": "배경 설정, 장소, 시간, 환경 등을 수정하세요.",
        "events": "게임 이벤트, 뉴스, 주식 변동 등을 수정하세요.",
        "dialogue": "캐릭터의 대화나 설명 텍스트를 수정하세요.",
        "general": "사용자 요청에 따라 관련 부분을 수정하세요."
    }
    
    instruction = modification_instructions.get(modification_type, modification_instructions["general"])
    
    return f"""
다음은 수정할 기존 스토리 데이터입니다:

{original_story_data}

사용자 요청: {user_request}

수정 지침: {instruction}

수정 사항:
1. 기존 스토리의 전체적인 구조와 흐름은 유지하세요
2. 요청된 부분만 정확히 수정하세요
3. 10세 이하 아동이 이해하기 쉬운 언어로 작성하세요
4. 투자 교육 목적에 맞게 수정하세요
5. JSON 형식을 정확히 유지하세요

수정된 전체 스토리 데이터를 JSON 형식으로 반환하세요:
"""