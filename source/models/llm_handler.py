"""
LLM 모델 관리 모듈 - LangChain with Google Gemini
"""
import os
import json
import re
import asyncio
from typing import Optional, Dict, Any, List, AsyncGenerator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
from source.utils.config import load_api_key, get_model_settings
import streamlit as st


class StreamingCallbackHandler(BaseCallbackHandler):
    """스트리밍을 위한 콜백 핸들러"""
    
    def __init__(self, container=None):
        self.container = container or st.empty()
        self.text = ""
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """새로운 토큰이 생성될 때 호출됩니다"""
        self.text += token
        self.container.markdown(self.text)


def initialize_llm():
    """
    LLM 모델을 초기화합니다.
    
    Returns:
        ChatGoogleGenerativeAI: 초기화된 LangChain Gemini 모델
    """
    api_key = load_api_key()
    if not api_key:
        raise ValueError("API 키를 불러올 수 없습니다.")
    
    settings = get_model_settings()
    
    # LangChain GoogleGenerativeAI 모델 초기화
    llm = ChatGoogleGenerativeAI(
        model=settings["model_name"],
        google_api_key=api_key,
        temperature=settings.get("temperature", 0.7),
        max_output_tokens=settings.get("max_tokens", 4096),
        top_p=settings.get("top_p", 0.9)
    )
    
    return llm


async def initialize_llm_async():
    """
    비동기 LLM 모델을 초기화합니다.
    
    Returns:
        ChatGoogleGenerativeAI: 초기화된 LangChain Gemini 모델
    """
    api_key = load_api_key()
    if not api_key:
        raise ValueError("API 키를 불러올 수 없습니다.")
    
    settings = get_model_settings()
    
    # LangChain GoogleGenerativeAI 모델 초기화 (비동기 지원)
    llm = ChatGoogleGenerativeAI(
        model=settings["model_name"],
        google_api_key=api_key,
        temperature=settings.get("temperature", 0.7),
        max_output_tokens=settings.get("max_tokens", 4096),
        top_p=settings.get("top_p", 0.9)
    )
    
    return llm


async def generate_game_data_async(prompt: str, llm: Optional[ChatGoogleGenerativeAI] = None) -> tuple:
    """
    비동기적으로 게임 스토리 데이터를 생성합니다.
    
    Args:
        prompt (str): 생성할 프롬프트
        llm (Optional[ChatGoogleGenerativeAI]): LLM 모델 인스턴스
        
    Returns:
        tuple: (생성된 스토리 데이터, 메타데이터)
    """
    if llm is None:
        llm = await initialize_llm_async()
    
    try:
        # 비동기 호출
        messages = [HumanMessage(content=prompt)]
        response = await llm.ainvoke(messages)
        
        # 응답 파싱
        content = response.content
        
        # JSON 추출 시도
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
                story_data = json.loads(json_content)
            else:
                # JSON 블록이 없다면 전체 내용에서 JSON 찾기
                story_data = json.loads(content)
        except json.JSONDecodeError:
            # JSON 파싱 실패시 텍스트 그대로 반환
            story_data = {"content": content, "type": "text"}
        
        metadata = {
            "model": llm.model_name,
            "tokens_used": len(content.split()),
            "async": True
        }
        
        return story_data, metadata
        
    except Exception as e:
        raise Exception(f"비동기 LLM 생성 중 오류 발생: {str(e)}")


async def generate_multiple_scenarios_async(
    prompts: List[str], 
    llm: Optional[ChatGoogleGenerativeAI] = None,
    max_concurrent: int = 3
) -> List[tuple]:
    """
    여러 시나리오를 병렬로 비동기 생성합니다.
    
    Args:
        prompts (List[str]): 프롬프트 리스트
        llm (Optional[ChatGoogleGenerativeAI]): LLM 모델 인스턴스
        max_concurrent (int): 최대 동시 실행 수
        
    Returns:
        List[tuple]: [(스토리 데이터, 메타데이터), ...]
    """
    if llm is None:
        llm = await initialize_llm_async()
    
    # 세마포어로 동시 실행 수 제한
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def generate_single(prompt: str):
        async with semaphore:
            return await generate_game_data_async(prompt, llm)
    
    # 모든 프롬프트를 병렬로 처리
    tasks = [generate_single(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 예외 처리
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append((
                {"error": str(result), "prompt_index": i}, 
                {"error": True, "async": True}
            ))
        else:
            processed_results.append(result)
    
    return processed_results


async def generate_game_data_stream(
    prompt: str, 
    container, 
    llm: Optional[ChatGoogleGenerativeAI] = None
) -> tuple:
    """
    스트리밍 방식으로 게임 데이터를 생성합니다.
    
    Args:
        prompt (str): 생성할 프롬프트
        container: Streamlit 컨테이너
        llm (Optional[ChatGoogleGenerativeAI]): LLM 모델 인스턴스
        
    Returns:
        tuple: (생성된 스토리 데이터, 메타데이터)
    """
    if llm is None:
        llm = await initialize_llm_async()
    
    try:
        # 스트리밍 콜백 핸들러 생성
        callback_handler = StreamingCallbackHandler(container)
        
        # 스트리밍 설정으로 LLM 호출
        messages = [HumanMessage(content=prompt)]
        
        # 스트리밍 호출 (동기 방식이지만 UI 업데이트는 실시간)
        response = llm.invoke(messages, callbacks=[callback_handler])
        
        # 최종 결과 파싱
        content = response.content
        
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
                story_data = json.loads(json_content)
            else:
                story_data = json.loads(content)
        except json.JSONDecodeError:
            story_data = {"content": content, "type": "text"}
        
        metadata = {
            "model": llm.model_name,
            "tokens_used": len(content.split()),
            "streaming": True
        }
        
        return story_data, metadata
        
    except Exception as e:
        container.error(f"스트리밍 생성 중 오류 발생: {str(e)}")
        raise Exception(f"스트리밍 LLM 생성 중 오류 발생: {str(e)}")


def create_prompt_template(system_message, user_template="{question}"):
    """
    LangChain 프롬프트 템플릿을 생성합니다.
    
    Args:
        system_message (str): 시스템 메시지
        user_template (str, optional): 사용자 템플릿. 기본값은 "{question}"
        
    Returns:
        PromptTemplate: LangChain 프롬프트 템플릿
    """
    template = f"""{system_message}

사용자 요청: {user_template}"""
    
    return PromptTemplate(
        input_variables=["question"],
        template=template
    )

def generate_game_data(llm, prompt_template, prompt_content):
    """
    게임 데이터를 생성합니다.
    
    Args:
        llm (ChatGoogleGenerativeAI): 초기화된 LangChain LLM 모델
        prompt_template (PromptTemplate): LangChain 프롬프트 템플릿
        prompt_content (str): 프롬프트 내용
        
    Returns:
        str: 생성된 게임 데이터 (JSON 문자열)
    """
    print("게임 시나리오 데이터 생성 중...")
    
    try:
        # LangChain을 사용한 프롬프트 생성 및 모델 호출
        formatted_prompt = prompt_template.format(question=prompt_content)
        
        # LangChain 메시지 체인 생성
        messages = [HumanMessage(content=formatted_prompt)]
        
        # 모델 호출
        response = llm.invoke(messages)
        
        # 응답 내용 확인
        content = response.content
        if not content or not content.strip():
            print("경고: LLM이 빈 응답을 반환했습니다.")
            return None
        
        # 응답 출력 (디버깅용)
        print("\nLLM 원본 응답:")
        print(content)
        
        # JSON 처리 로직은 기존과 동일
        return _process_llm_response(content)
        
    except Exception as e:
        print(f"LLM 데이터 생성 중 오류 발생: {e}")
        return None

async def generate_game_data_async(llm, prompt_template, prompt_content):
    """
    게임 데이터를 비동기로 생성합니다.
    
    Args:
        llm (ChatGoogleGenerativeAI): 초기화된 LangChain LLM 모델
        prompt_template (PromptTemplate): LangChain 프롬프트 템플릿
        prompt_content (str): 프롬프트 내용
        
    Returns:
        str: 생성된 게임 데이터 (JSON 문자열)
    """
    print("게임 시나리오 데이터 생성 중... (비동기)")
    
    try:
        # LangChain을 사용한 프롬프트 생성 및 모델 호출
        formatted_prompt = prompt_template.format(question=prompt_content)
        
        # LangChain 메시지 체인 생성
        messages = [HumanMessage(content=formatted_prompt)]
        
        # 비동기 모델 호출
        response = await llm.ainvoke(messages)
        
        # 응답 내용 확인
        content = response.content
        if not content or not content.strip():
            print("경고: LLM이 빈 응답을 반환했습니다.")
            return None
        
        # 응답 출력 (디버깅용)
        print("\nLLM 원본 응답:")
        print(content)
        
        # JSON 처리 로직은 기존과 동일
        return _process_llm_response(content)
        
    except Exception as e:
        print(f"LLM 데이터 생성 중 오류 발생: {e}")
        return None

def _process_llm_response(content):
    """
    LLM 응답을 처리하여 JSON 형식으로 변환합니다.
    """
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
    try:
        # 직접 JSON 파싱 시도
        json.loads(cleaned_content)
        print("유효한 JSON 형식 확인됨!")
        return cleaned_content
    except json.JSONDecodeError:
        print("JSON 파싱 실패, JSON 형식 추출 시도...")
        
        # JSON 구조 추출 시도
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

# 병렬 처리를 위한 함수들
async def generate_multiple_scenarios_async(llm, prompt_template, prompt_contents):
    """
    여러 시나리오를 병렬로 생성합니다.
    
    Args:
        llm: LLM 모델
        prompt_template: 프롬프트 템플릿
        prompt_contents (list): 프롬프트 내용 리스트
        
    Returns:
        list: 생성된 시나리오 데이터 리스트
    """
    tasks = []
    for content in prompt_contents:
        task = generate_game_data_async(llm, prompt_template, content)
        tasks.append(task)
    
    # 병렬 실행
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 예외 처리
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"시나리오 {i+1} 생성 실패: {result}")
            processed_results.append(None)
        else:
            processed_results.append(result)
    
    return processed_results

# 스트리밍 처리를 위한 함수
async def generate_game_data_stream(llm, prompt_template, prompt_content, callback=None):
    """
    게임 데이터를 스트리밍으로 생성합니다.
    
    Args:
        llm: LLM 모델
        prompt_template: 프롬프트 템플릿
        prompt_content: 프롬프트 내용
        callback: 토큰별 콜백 함수
        
    Returns:
        str: 최종 생성된 게임 데이터
    """
    print("게임 시나리오 데이터 스트리밍 생성 중...")
    
    try:
        formatted_prompt = prompt_template.format(question=prompt_content)
        messages = [HumanMessage(content=formatted_prompt)]
        
        full_response = ""
        
        # 스트리밍 처리
        async for chunk in llm.astream(messages):
            if chunk.content:
                full_response += chunk.content
                if callback:
                    await callback(chunk.content)
        
        return _process_llm_response(full_response)
        
    except Exception as e:
        print(f"스트리밍 생성 중 오류 발생: {e}")
        return None
