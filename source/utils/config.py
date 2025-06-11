"""
설정 및 환경 변수 관리 모듈
"""
import os
import streamlit as st
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_api_key():
    """
    API 키를 환경변수에서 로드합니다.
    Streamlit Cloud Secrets 우선, 로컬 .env 대안
    
    Returns:
        str: Google Gemini API 키
    """
    try:
        # Streamlit Cloud Secrets 우선
        if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
            logger.info("Streamlit Secrets에서 API 키 로드")
            return st.secrets['GOOGLE_API_KEY']
    except Exception as e:
        logger.warning(f"Streamlit Secrets 로드 실패: {e}")
    
    try:
        # 로컬 환경 대안
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            logger.info("로컬 환경변수에서 API 키 로드")
            return api_key
        else:
            logger.error("환경변수에서 GOOGLE_API_KEY를 찾을 수 없습니다")
            return None
    except Exception as e:
        logger.error(f"API 키 로드 중 오류 발생: {e}")
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
