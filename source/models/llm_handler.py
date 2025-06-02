"""
LLM 모델 관리 모듈
"""
import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from source.utils.config import load_api_key, get_model_settings

def initialize_llm():
    """
    LLM 모델을 초기화합니다.
    
    Returns:
        ChatOpenAI: 초기화된 ChatOpenAI 모델
    """
    api_key = load_api_key()
    if not api_key:
        raise ValueError("API 키를 불러올 수 없습니다.")
    
    os.environ["OPENAI_API_KEY"] = api_key
    settings = get_model_settings()
    
    return ChatOpenAI(
        model=settings["model_name"],
        temperature=settings["temperature"],
        max_tokens=settings["max_tokens"]
    )

def create_prompt_template(system_message, user_template="{question}"):
    """
    프롬프트 템플릿을 생성합니다.
    
    Args:
        system_message (str): 시스템 메시지
        user_template (str, optional): 사용자 템플릿. 기본값은 "{question}"
        
    Returns:
        ChatPromptTemplate: 생성된 프롬프트 템플릿
    """
    return ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", user_template)
    ])

def generate_game_data(llm, prompt_template, prompt_content):
    """
    게임 데이터를 생성합니다.
    
    Args:
        llm (ChatOpenAI): 초기화된 LLM 모델
        prompt_template (ChatPromptTemplate): 프롬프트 템플릿
        prompt_content (str): 프롬프트 내용
        
    Returns:
        str: 생성된 게임 데이터 (JSON 문자열)
    """
    print("게임 시나리오 데이터 생성 중...")
    try:
        chain = prompt_template | llm
        response = chain.invoke({"question": prompt_content})
        
        # 응답 내용 확인
        content = response.content
        if not content or not content.strip():
            print("경고: LLM이 빈 응답을 반환했습니다.")
            return None
        
        # 응답 출력 (디버깅용)
        print("\nLLM 원본 응답:")
        print(content)
        
        # 마크다운 코드 블록 처리
        cleaned_content = content.strip()
        
        # JSON, javascript, js 등의 마크다운 코드 블록 제거
        if cleaned_content.startswith("```"):
            # 첫 번째 줄과 마지막 줄 제거
            lines = cleaned_content.split("\n")
            if len(lines) >= 3:  # 최소한 3줄 이상 (시작 태그, 내용, 종료 태그)
                if lines[0].startswith("```") and "```" in lines[-1]:
                    # 첫 줄이 ```json, ```javascript 등으로 시작하면 제거
                    # 마지막 줄에 ``` 포함되어 있으면 제거
                    cleaned_content = "\n".join(lines[1:-1])
                    print("코드 블록 마크다운 제거됨")
        
        # 앞뒤 공백 제거
        cleaned_content = cleaned_content.strip()
        
        # JSON 형식 확인 및 추출
        import json
        try:
            # 직접 JSON 파싱 시도
            json.loads(cleaned_content)
            print("유효한 JSON 형식 확인됨!")
            return cleaned_content
        except json.JSONDecodeError:
            print("JSON 파싱 실패, JSON 형식 추출 시도...")
            
            # JSON 구조 추출 시도
            import re
            # 가장 외부 대괄호를 포함한 전체 JSON 배열 찾기
            json_array_pattern = r'(\[\s*\{.*\}\s*\])'
            array_match = re.search(json_array_pattern, cleaned_content, re.DOTALL)
            
            if array_match:
                json_content = array_match.group(1)
                print(f"JSON 배열 구조 추출 성공! (길이: {len(json_content)})")
                
                # 추출된 JSON 유효성 확인
                try:
                    json.loads(json_content)
                    print("추출된 JSON 유효성 확인됨!")
                    return json_content
                except json.JSONDecodeError as e:
                    print(f"추출된 JSON 구조 파싱 실패: {e}")
            
            # 대안: 개별 JSON 객체들 찾기
            objects_pattern = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
            objects = re.findall(objects_pattern, cleaned_content, re.DOTALL)
            
            if objects:
                try:
                    # 객체들을 배열로 묶기
                    json_array = "[" + ",".join(objects) + "]"
                    json.loads(json_array)  # 유효성 확인
                    print(f"개별 JSON 객체 {len(objects)}개를 배열로 결합 성공!")
                    return json_array
                except json.JSONDecodeError:
                    print("JSON 객체 결합 실패")
            
            print("응답에서 유효한 JSON 구조를 찾을 수 없습니다.")
            return None
        
    except Exception as e:
        print(f"LLM 데이터 생성 중 오류 발생: {e}")
        return None
