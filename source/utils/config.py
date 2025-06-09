"""
설정 및 환경 변수 관리 모듈
"""
import os
from dotenv import load_dotenv

def load_api_key():
    """
    API 키를 환경변수에서 로드합니다.
    
    Returns:
        str: Google Gemini API 키
    """
    try:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        return api_key
    except Exception as e:
        print(f"API 키 로드 중 오류 발생: {e}")
        return None

def get_model_settings():
    """
    모델 설정값을 반환합니다.
    
    Returns:
        dict: 모델 설정값
    """
    return {
        "model_name": "gemini-2.5-flash-preview-05-20",
        "temperature": 1,
        "max_tokens": 65000
    }
