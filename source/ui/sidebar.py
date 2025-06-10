"""
사이드바 UI 컴포넌트 - 간소화된 버전
"""
import streamlit as st
from source.utils.config import load_api_key


def render_sidebar():
    """간소화된 사이드바 렌더링"""
    with st.sidebar:
        st.header("🎯 스토리 편집기")
        
        # 편집 모드 정보
        st.success("✏️ **편집 모드**")
        st.info("메인 화면에서 스토리를 선택하고 AI와 함께 편집해보세요!")
        
        st.markdown("---")
        
        # API 상태
        st.subheader("🔧 시스템 상태")
        api_key = load_api_key()
        if api_key:
            st.success("✅ Google API 연결됨")
        else:
            st.error("❌ API 키 없음")
            st.info("`.env` 파일에 `GOOGLE_API_KEY` 설정 필요")
        
        # 세션 상태 확인
        if st.session_state.get('current_game_data'):
            st.success("✅ 스토리 로드됨")
        else:
            st.warning("⏳ 스토리 선택 대기")
    
    return None