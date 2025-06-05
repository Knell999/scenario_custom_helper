"""
스토리 게임 커스터마이저 - 메인 애플리케이션
"""
import streamlit as st
import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 모듈 import
from source.components.game_customizer import GameCustomizer
from source.ui.sidebar import render_sidebar
from source.ui.chat_interface import render_chat_interface
from source.ui.story_viewer import render_story_viewer
from source.ui.info_tabs import render_info_tabs
from source.utils.config import load_api_key


def initialize_session_state():
    """세션 상태 초기화"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_game_data' not in st.session_state:
        st.session_state.current_game_data = None
    
    if 'customizer' not in st.session_state:
        st.session_state.customizer = GameCustomizer()
        
    # 편집 모드로 고정
    if 'work_mode' not in st.session_state:
        st.session_state.work_mode = "edit"
        
    if 'investment_focus' not in st.session_state:
        st.session_state.investment_focus = "story_editing"


def check_api_key():
    """API 키 확인"""
    api_key = load_api_key()
    if not api_key:
        st.error("⚠️ OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 설정해주세요.")
        st.stop()
    return api_key


def setup_page():
    """페이지 설정"""
    st.set_page_config(
        page_title="🎮 투자 교육 스토리 편집기",
        page_icon="✏️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 페이지 헤더
    st.title("🎮 투자 교육 스토리 편집기")
    st.markdown("기존 스토리를 AI와 함께 수정하고 개선해보세요!")


def main():
    """메인 애플리케이션"""
    # 페이지 설정
    setup_page()
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # API 키 확인
    check_api_key()
    
    # 사이드바 렌더링
    render_sidebar()
    
    # 메인 컨텐츠 영역
    col1, col2 = st.columns([1, 1])
    
    # 왼쪽: 채팅 인터페이스
    with col1:
        st.subheader("💬 AI 스토리 편집기")
        render_chat_interface(st.session_state.customizer)
    
    # 오른쪽: 스토리 뷰어
    with col2:
        st.subheader("📖 스토리 미리보기")
        render_story_viewer(st.session_state.customizer)
    
    # 하단: 정보 탭들
    render_info_tabs()


if __name__ == "__main__":
    main()
