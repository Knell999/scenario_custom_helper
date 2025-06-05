"""
사이드바 UI 컴포넌트
"""
import streamlit as st
from source.utils.config import load_api_key
from source.utils.story_manager import StoryManager


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.header("🎯 스토리 편집 설정")
        
        # 편집 모드로 고정
        st.session_state.work_mode = "edit"
        st.session_state.investment_focus = "story_editing"
        st.info("💡 저장된 스토리를 선택하고 수정할 수 있습니다.")
        
        st.markdown("---")
        
        # 스토리 관리
        st.header("📚 저장된 스토리")
        
        # 스토리 매니저 초기화
        if 'story_manager' not in st.session_state:
            st.session_state.story_manager = StoryManager()
        
        # 저장된 스토리 목록
        saved_stories = st.session_state.story_manager.get_saved_stories()
        
        if saved_stories:
            story_names = [f"{story['metadata']['story_name']} ({story['metadata']['scenario_type']})" 
                          for story in saved_stories]
            
            selected_story_index = st.selectbox(
                "저장된 스토리 선택",
                range(len(story_names)),
                format_func=lambda x: story_names[x] if x < len(story_names) else "선택하세요"
            )
            
            col_load, col_delete = st.columns(2)
            
            with col_load:
                if st.button("📖 불러오기", type="primary"):
                    selected_story_info = saved_stories[selected_story_index]
                    # Load the full story from file
                    loaded_story = st.session_state.story_manager.load_story(selected_story_info['filepath'])
                    
                    # Handle both old format (direct array) and new format (with metadata)
                    if isinstance(loaded_story, list):
                        # Old format: direct array of game data
                        st.session_state.current_game_data = loaded_story
                        story_name = selected_story_info['filename'].replace('.json', '')
                    else:
                        # New format: with metadata wrapper
                        st.session_state.current_game_data = loaded_story['story_data']
                        story_name = loaded_story['metadata'].get('story_name', selected_story_info['filename'].replace('.json', ''))
                    
                    st.success(f"'{story_name}' 스토리를 불러왔습니다!")
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️ 삭제", type="secondary"):
                    story_filepath = saved_stories[selected_story_index]['filepath']
                    if st.session_state.story_manager.delete_story(story_filepath):
                        st.success("삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("삭제 실패")
        else:
            st.info("저장된 스토리가 없습니다.")
        
        st.markdown("---")
        
        # API 키 확인
        api_key = load_api_key()
        if api_key:
            st.success("✅ API 키 로드됨")
        else:
            st.error("❌ API 키를 찾을 수 없습니다")
            st.info("`.env` 파일에 `OPENAI_API_KEY`를 설정해주세요")        
    return None  # scenario_type 반환하지 않음
