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
        
        # 편집 가이드
        st.subheader("💡 편집 팁")
        st.write("""
        **🎭 캐릭터 수정**
        • "캐릭터 이름을 바꿔줘"
        • "성격을 더 친근하게 해줘"
        
        **🌍 배경 수정**  
        • "배경을 우주로 바꿔줘"
        • "계절을 겨울로 설정해줘"
        
        **📖 내용 수정**
        • "3턴 이벤트를 더 재미있게"
        • "설명을 더 쉽게 바꿔줘"
        """)
        
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
